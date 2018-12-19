import * as state_handler from "./state_handler";
import * as substitution_tree_worker from "./substitution_tree_worker"
import {states} from "./state_handler";
import {notify_open} from "./layout";

export { register };

function register(myLayout) {
    myLayout.registerComponent('substitution_tree', function (container, componentState) {
        container.getElement().html(`
            <div class="content">
                <div class="header">
                <div class="btn-group">
                    <button type="button" data-id="${componentState.id}" 
                            class="btn btn-sm btn-secondary prev">Prev</button>          
                    <button type="button" data-id="${componentState.id}" 
                            class="btn btn-sm btn-secondary next">Next</button>
                </div>            
                <div class="btn-group">
                    <button type="button" data-id="${componentState.id}" 
                            class="btn btn-sm btn-secondary prev-expr">Prev Expr</button>          
                    <button type="button" data-id="${componentState.id}" 
                            class="btn btn-sm btn-secondary next-expr">Next Expr</button>
                </div>
                </div>
                <div class="tree">
                    <svg></svg>
                </div>
            </div>
        `);

        let rawSVG = container.getElement().find(".tree > svg").get(0);
        // svgPanZoom(rawSVG, {fit: false, zoomEnabled: true, center: false, controlIconsEnabled: true});
        let svg = SVG.adopt(rawSVG).size(container.width, container.height);
        console.log("adopted");
        let ready = false;

        container.on("open", function () {
            notify_open("substitution_tree", container);
        });

        container.getElement().find(".tree").on("update", function (e) {
            let zoom = svgPanZoom(rawSVG).getZoom();
            let pan = svgPanZoom(rawSVG).getPan();
            svgPanZoom(rawSVG).destroy();
            console.log(rawSVG === undefined);
            console.log(jQuery.isReady);
            if (ready) {
                svg.clear();
            } else {
                ready = true;
                console.log("SKIP");
            }
            substitution_tree_worker.display_tree(componentState.id, svg);
            svgPanZoom(rawSVG, {fit: false, zoomEnabled: true, center: false, controlIconsEnabled: true});
            if (isNaN(zoom)) {
                svgPanZoom(rawSVG).reset();
            } else {
                svgPanZoom(rawSVG).zoom(zoom);
                svgPanZoom(rawSVG).pan(pan);
            }
        });

        container.getElement().find(".tree").on("reset", function () {
            svgPanZoom(rawSVG).reset();
            console.log("reset!");
        });

        container.on("resize", function () {
            let zoom = svgPanZoom(rawSVG).getZoom();
            let pan = svgPanZoom(rawSVG).getPan();
            svgPanZoom(rawSVG).destroy();
            svg.size(container.width, container.height);
            console.log("ready!");
            svgPanZoom(rawSVG, {fit: false, zoomEnabled: true, center: false, controlIconsEnabled: true});
            if (isNaN(zoom)) {
                svgPanZoom(rawSVG).reset();
            } else {
                svgPanZoom(rawSVG).zoom(zoom);
                svgPanZoom(rawSVG).pan(pan);
            }
        });

        container.on("destroy", function () {
            states[componentState.id].sub_open = false;
            notify_open("substitution_tree", container);
        });
    });
}