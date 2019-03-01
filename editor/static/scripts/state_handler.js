import {begin_slow, end_slow} from "./event_handler";
import {getLayout, open, setLayout} from "./layout";
import {getAllSettings, setAllSettings} from "./settings";

export {states, temp_file, loadState, saveState, make_new_state};

let base_state = {
    states: {},
    environments: [],
    moves: [],
    out: "",
    heap: {},
    frameUpdates: [],

    index: 0,
    expr_i: 0,

    start: 0,
    end: 0,
    roots: ["demo"],

    globalFrameID: -1,

    editor_open: false,
    sub_open: false,
    env_open: false,
    turtle_open: false,
    out_open: false,
    tests_open: false,

    active_code: "",
    up_to_date: true,

    test_results: undefined,

    file_name: "",
};

let skip_saves = ["states", "environments", "moves", "out", "heap", "frameUpdates"];

let states = [make_new_state()];
states[0].file_name = $.parseJSON(start_data)["file"];

let temp_file = "__";

function make_new_state() {
    return jQuery.extend(true, {}, base_state);
}

async function loadState() {
    begin_slow();
    await $.post("./load_state", {})
        .done(function (data) {
            end_slow();
            if (data !== "fail") {
                data = $.parseJSON(data);
                states = data.states;
                setLayout(data.layout);
                setAllSettings(data.settings);
            }
        });
}

let curr_saving = false;
async function saveState(full=false, layout=undefined) {
    if (curr_saving) {
        return;
    }
    begin_slow();
    curr_saving = true;
    if (layout === undefined) {
        layout = getLayout();
    }

    let temp = [];

    if (full) {
        temp = states;
    } else {
        for (let state of states) {
            temp.push(jQuery.extend({}, state)); // shallow copy
        }

        for (let state of temp) {
            for (let key of skip_saves) {
                delete state[key];
            }
        }
    }

    await $.post("./save_state", {
        state: JSON.stringify({states: temp, layout: layout, settings: getAllSettings()}),
    }).done(function () {
        curr_saving = false;
        end_slow();
    });
}
