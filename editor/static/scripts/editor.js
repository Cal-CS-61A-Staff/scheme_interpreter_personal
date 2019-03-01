import {saveState, states, temp_file} from "./state_handler";

import {notify_close, open, open_prop} from "./layout";
import {begin_slow, end_slow, make, request_update} from "./event_handler";

export {register};

function register(layout) {
    layout.registerComponent('editor', function (container, componentState) {
        container.getElement().html(`
        <div class="content">
            <div class="header">        
                ${(!states[componentState.id].file_name.startsWith(temp_file)) ?
            `<button type="button" class="btn-light save-btn" aria-label="Save">
                    <span class="text"> Save </span>
                </button>` : ``}


                <button type="button" data-toggle="tooltip"
                            title="Open a console and run the program locally."
                            class="btn-success toolbar-btn run-btn">Run</button>
                ${(componentState.id === 0) ?
            `<button type="button" data-toggle="tooltip"
                            title="Run all ok.py tests locally."
                            class="btn-danger toolbar-btn test-btn">Test</button>` : ``}
                <button type="button" data-toggle="tooltip"
                            title="Step through the program's execution."
                            class="btn-primary toolbar-btn sub-btn">Debug</button>          
                <button type="button" data-toggle="tooltip"
                            title="View environment diagram."
                            class="btn-info toolbar-btn env-btn">Environments</button>          
                <button type="button" data-toggle="tooltip"
                            title="Reformat code and fix (some) minor mistakes."
                            class="btn-secondary toolbar-btn reformat-btn">Reformat</button>          
            </div>
            <div class="editor-wrapper">
                <div class="editor"></div>
            </div>
        </div>
    `);

        make(container, "editor", componentState.id);

        let editorDiv;
        let editor;

        let changed = false;
        let saveTimer;

        container.on("open", function () {
            editorDiv = container.getElement().find(".editor").get(0);
            editor = ace.edit(editorDiv);
            ace.config.set("packaged", true);
            editor.session.setMode("ace/mode/scheme");
            editor.setOption("fontSize", 14);
            editor.setOption("enableBasicAutocompletion", true);
            editor.setOption("enableLiveAutocompletion", true);
            editor.setAutoScrollEditorIntoView(true);
            editor.getSession().setUseSoftTabs(true);
            editor.container.style.background = "white";
            editor.focus();

            saveTimer = setInterval(save, 5000);

            states[componentState.id].editor_open = true;

            container.on("resize", function () {
                editor.resize();
            });

            let decoded = $.parseJSON(start_data);
            if (componentState.id === 0) {
                states[componentState.id].file_name = decoded["file"];
            }

            if (states[componentState.id].file_name.startsWith(temp_file)) {
                editor.setValue(states[componentState.id].file_content);
            } else {
                $.post("/read_file", {
                    filename: states[componentState.id].file_name,
                }).done(function (data) {
                    data = $.parseJSON(data);
                    editor.setValue(data);
                });
            }

            editor.getSession().on("change", function () {
                container.getElement().find(".save-btn > .text").text("Save");
                changed = true;
            });
        });

        container.getElement().on("update", function (e) {
            if (e.target !== e.currentTarget) {
                return;
            }
            if (states[componentState.id].environments.length === 0) {
                // program has never been run
                container.getElement().find(".env-btn")//.prop("disabled", true)
                .attr('data-original-title', "To use the environment diagram, press Run first.");
                container.getElement().find(".sub-btn")//.prop("disabled", true)
                .attr('data-original-title', "To use the debugger, press Run first.");
            } else {
                container.getElement().find(".env-btn")//.prop("disabled", false)
                .attr('data-original-title', "View environment diagram.");
                container.getElement().find(".sub-btn")//.prop("disabled", false)
                .attr('data-original-title', "Step through the program's execution.");
            }
        });

        container.on("destroy", function () {
            clearInterval(saveTimer);
        });


        container.getElement().keydown(function (event) {
            if ((event.ctrlKey || event.metaKey) && event.keyCode === 13) {
                event.preventDefault();
                // noinspection JSIgnoredPromiseFromCall
                run();
            }
            if ((event.ctrlKey || event.metaKey) && event.keyCode === 83) {
                event.preventDefault();
                // noinspection JSIgnoredPromiseFromCall
                save();
            }
        });

        container.getElement().find(".run-btn").on("click", run);

        container.getElement().find(".save-btn").on("click", save);

        container.getElement().find(".reformat-btn").on("click", reformat);

        container.getElement().find(".sub-btn").on("click", async function () {
            await save();
            open("substitution_tree", componentState.id);
        });

        container.getElement().find(".env-btn").on("click", async function () {
            await save();
            open("env_diagram", componentState.id);
        });

        container.getElement().find(".test-btn").on("click", run_tests);

        async function save(running) {
            if (states[componentState.id].file_name.startsWith(temp_file) || (!running && (!changed))) {
                return;
            }
            container.getElement().find(".save-btn > .text").text("Saving...");

            let code = [editor.getValue()];
            await $.post("./save", {
                code: code,
                filename: states[componentState.id].file_name,
            }).done(function (data) {
                data = $.parseJSON(data);
                if (data["result"] === "success") {
                    container.getElement().find(".save-btn > .text").text("Saved");
                    changed = false;
                    if (running) {
                        states[componentState.id].active_code = data["stripped"];
                        states[componentState.id].up_to_date = true;
                        return;
                    }
                    if (states[componentState.id].active_code === data["stripped"]) {
                        if (!states[componentState.id].up_to_date) {
                            states[componentState.id].up_to_date = true;
                            request_update();
                        } else {
                            states[componentState.id].up_to_date = true;
                        }
                    } else {
                        states[componentState.id].up_to_date = false;
                    }
                } else {
                    alert("Save error - try copying code from editor to a file manually");
                }
            });
        }

        async function run() {
            if (editor.getValue().trim() === "") {
                return;
            }
            let code = [editor.getValue()];
            begin_slow();
            $.post("./process2", {
                code: code,
                globalFrameID: -1,
                curr_i: 0,
                curr_f: 0,
            }).done(async function (data) {
                end_slow();
                data = $.parseJSON(data);
                if (data.success) {
                    states[componentState.id].states = data.states;
                    states[componentState.id].environments = [];
                    for (let key of data.active_frames) {
                        states[componentState.id].environments.push(data.frame_lookup[key]);
                    }
                    states[componentState.id].moves = data.graphics;
                    states[componentState.id].out = data.out[0];
                    states[componentState.id].start = data.states[0][0];
                    states[componentState.id].end = data.states[0][1];
                    states[componentState.id].index = data.states[0][0];
                    states[componentState.id].expr_i = 0;
                    states[componentState.id].roots = data.roots;
                    states[componentState.id].globalFrameID = data.globalFrameID;
                    states[componentState.id].heap = data.heap;
                    states[componentState.id].frameUpdates = data.frameUpdates;
                } else {
                    states[componentState.id].out = data.out[0];
                }

                await save(true);

                await open("output", componentState.id);
                // noinspection JSIgnoredPromiseFromCall
                saveState(true);
                $("*").trigger("reset");
                request_update();
            });
        }

        function reformat() {
            let code = [editor.getValue()];
            $.post("./reformat", {
                code: code,
            }).done(function (data) {
                data = $.parseJSON(data);
                if (data["result"] === "success") {
                    editor.setValue(data["formatted"]);
                } else {
                    alert("An error occurred!");
                }
            });
        }

        function run_tests() {
            if (editor.getValue().trim() === "") {
                return;
            }
            let code = [editor.getValue()];
            begin_slow();
            $.post("./test", {
                code: code,
                filename: states[componentState.id].file_name,
            }).done(async function (data) {
                end_slow();
                data = $.parseJSON(data);
                states[componentState.id].test_results = data;
                await save();
                open("test_results", componentState.id);
            });
        }
    });
}