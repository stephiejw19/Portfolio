// Code was copied from http://johnguerra.co/viz/berkeleyFinalProjectsSummer2018/
// Code inspired on VisualCinamon http://blockbuilder.org/john-guerra/e5d5fbb6c526000599d2c83639f6ade0
function ProjectsComb() {
    /* global d3, CombColumns */

    var comb = {};
    var width = 50,
        height = 60, // Only used if fixedRows is true
        margin = {top: 70, right: 0, bottom: 50, left: 40 },
        //The number of columns and rows of the comb
        MapColumns = 2,
        MapRows = 2,
        fixedWidth = false, // Compute the width from the parent object
        fixedRows = true, // Compute the rows or have a fixed number?
        repeat = true, // Repeat the projects in the "background"?
        fade = true, // Fadeout hexes on mouseover
        containerID = "#comb",
        // thumbFn = function (d) { return "img/year_thumbnail.png"; },
        // textFn = function (d) { return d.project; },
        // onClick = function (d) { window.open(d.url, "_blank"); },
        hexbin = d3.hexbin();

    //Create SVG element
    d3.select(containerID).append("svg")
    // .style("width", "100%")
    // .style("height", "100%")
    // .attr("width", width + margin.left + margin.right)
    // .attr("height", height + margin.top + margin.bottom)
        .append("defs")
        .append("clipPath")
        .attr("id","hexClip")
        .append("path");

    var svg = d3.select(containerID + " > svg")
        .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    var projects = svg.append("g")
        .attr("class", "projects");
    var mesh = svg.append("path")
        .attr("class", "mesh");


    //Function to call when you mouseover a node
    function mover(d) {
        if (!d.important) return;
        d3.select(this)
            .transition()
            .duration(10)
            .style("opacity", 0.3);
        console.log(d);
    }

    //Mouseout function
    function mout(d) {
        if (!d.important) return;
        d3.select(this)
            .transition()
            .duration(1000)
            .style("opacity", 1);
    }

    function updateComb(data) {
        console.log("updateComb");
        if (!fixedWidth) {
            var svgNode = d3.select(containerID).node();
            width = svgNode ? svgNode.clientWidth : width;
        }

        // height = d3.select("#achievementsText").node() ? d3.select("#achievementsText").node().clientHeight: height;
        var hexRadius = width/((MapColumns + 0.5) * Math.sqrt(3));

        if (!fixedRows) {
            MapRows = Math.floor((height)/(1.5*hexRadius))+1;
        } else {
            height = (MapRows+1) * 1.5 * hexRadius;
        }


        d3.select(containerID + " > svg")
            .attr("width", width + margin.left + margin.right)
            .attr("height", height + margin.top + margin.bottom);

        var centers = hexbin
            .radius(hexRadius)
            .size([width, height])
            .centers();

        d3.select(containerID + " > svg #hexClip > path")
            .attr("transform", "translate(" + (Math.sin(Math.PI/3) * hexRadius) + "," + hexRadius+")")
            .attr("d", function () { return hexbin.hexagon(); });

        var fillingI = 0, importantI = data.length-1; // Two indexes to fill the comb
        // Do smart assigment, don't put a project on a cut hexagon
        centers.forEach(function (center, i) {
            center.j = Math.round(center[1] / (hexRadius * 1.5));
            center.i = Math.round((center[0] - (center.j & 1) * hexRadius * Math.sin(Math.PI / 3)) / (hexRadius * 2 * Math.sin(Math.PI / 3)));
            center.x = center[0] - Math.sin(Math.PI/3) * hexRadius;
            center.y = center[1] - hexRadius;
            center.proj = null;

            var even = center.j%2===0;
            var lastRow = fixedRows ? MapRows+1 : MapRows-1;
            var proj ;
            if ( (even && center.i=== 0) ||
                (!even && center.i>=MapColumns) ||
                center.j===0 ||
                center.j===lastRow) {

                center.important = false;
                // Unimportant projects here
                proj = repeat ? data[fillingI++%data.length] : null;

            } else {

                center.important = true;
                if (!repeat && importantI < 0) return; // We ran out of projects
                proj = data[importantI--];
                if (importantI<0 && repeat) {
                    importantI = data.length-1;
                }

            }
            if (proj)
                proj.index = i;
            center.proj = proj;
        });


        var projectsSel = projects.selectAll(".projectHex")
            .data(centers);

        var projectsSelEnter = projectsSel.enter()
            .append("g")
            .attr("class", "projectHex");

        projectsSelEnter
            .merge(projectsSel)
            .classed("important" , function (d) { return d.important; });


        // // Backgrounds
        // projectsSelEnter
        //   .append("rect")
        //   .attr("class", "hexBG")
        //   .merge(projectsSel.select(".hexBG"))
        //     .attr("clip-path", "url(#hexClip)")
        //     .attr("transform", function (d) {
        //       return "translate(" + d.x + "," + d.y + ")";
        //     })
        //     .attr("width", (hexRadius*2))
        //     .attr("height", (hexRadius*2));


        //Heading
        projectsSelEnter
            .append("text")
            .merge(projectsSel.select("text"))
            .filter(function (d) { return d.proj!==null; })
            .attr("x", (d)=>(d.x))
            .attr("y", (d)=>(d.y))
            .attr("font-size", "15px")
            .attr("dy",-70)
            .attr("dx",-35)
            .text((d)=>(d.proj.title));

        // Images
        projectsSelEnter
            .append("image")
            .merge(projectsSel.select("image"))
            .filter(function (d) { return d.proj!==null; })
            .attr("preserveAspectRatio", "xMinYMin slice")
            // .attr("viewPort", "0 0 " + (hexRadius*2)  + " " + (hexRadius*2))
            .attr("xlink:href", function (d) { return thumbFn(d.proj); })
            .attr("width", (hexRadius*2))
            .attr("height", (hexRadius*2))
            .attr("clip-path", "url(#hexClip)")
            .attr("transform", function (d) {
                // console.log("coordinate: (" + d.x + "," + d.y + ")");
                return "translate(" + d.x + "," + d.y + ")";
            })
            .on("click", function (d) { return onClick(d.proj); })
            .on("mouseover", mover)
            .on("mouseout", mout)

        projectsSelEnter
            .append("title")
            .filter(function (d) { return d.proj!==null; })
            .text(function (d) { return textFn(d.proj); });


        projectsSel.exit().remove();


        d3.select(".mesh").attr("d", hexbin.mesh);


        d3.select(window)
            .on("resize", function () { updateComb(data); });
        // .each(function () { updateComb(data); });

    }

    comb.columns = function(_) {
        if (arguments.length) { MapColumns=_; return comb; } else return MapColumns;
    };
    comb.rows = function(_) {
        if (arguments.length) { fixedRows = true; MapRows =_; return comb; } else return MapRows ;
    };
    comb.containerID = function(_) {
        if (arguments.length) { containerID=_; return comb; } else return containerID;
    };
    comb.textFn = function(_) {
        if (arguments.length) { textFn=_; return comb; } else return textFn;
    };
    comb.thumbFn = function(_) {
        if (arguments.length) { thumbFn=_; return comb; } else return thumbFn;
    };
    comb.onClick = function(_) {
        if (arguments.length) { onClick =_; return comb; } else return onClick ;
    };
    comb.height = function(_) {
        if (arguments.length) { fixedRows = false; height =_; return comb; } else return height ;
    };
    comb.width = function(_) {
        if (arguments.length) { fixedWidth = true; width =_; return comb; } else return width ;
    };
    comb.repeat = function(_) {
        if (arguments.length) { repeat =_; return comb; } else return repeat ;
    };

    comb.updateComb = updateComb;

    return comb;
}
