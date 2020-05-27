/* globals d3, ProjectsComb */

var width = d3.select("#comb").node().clientWidth,
    comb = ProjectsComb()
        .width(500)
        .columns(6)
        .rows(1)
        .containerID("#comb")
        .thumbFn(function (d) {
            console.log(d["thumbnail"]);
            return "img/" + d["thumbnail"];
        })
        .onClick(function (d) {
            showViz(d["tableau_share_id"], d["summary"]);
        })
        // .onClick(function (d) { return document.getElementById(d["Project title"].split(" ")[0]).scrollIntoView(); })
        .textFn(function (d) { return d["summary"]; })
        .repeat(false);

function updateBackground(data) {
    console.log(data);

    var columns = data.columns;
    var table = d3.select("#BackgroundTbl")
    var thead = table.append('thead')
    var tbody = table.append('tbody')

    thead.append('tr')
        .selectAll('th')
        .data(columns)
        .enter()
        .append('th')
        .text(function (d) { return d })

    var rows = tbody.selectAll('tr')
        .data(data)
        .enter()
        .append('tr')

    var cells = rows.selectAll('td')
        .data(function(row) {
            return columns.map(function (column) {
                return { column: column, value: row[column] }
            })
        })
        .enter()
        .append('td')
        .text(function (d) { return d.value })

    return table;
}

function update(data) {
    comb.updateComb(data);
    console.log(data);

    d3.selectAll("#viz").style("display", "none");
}

var viz;
function showViz(tableau_share_id, summary){

    d3.select("#vizIntro")
        .attr("hidden", true);

    if(!viz){
        d3.selectAll("#viz1563725193860")
            .style("width", "100%")
            .style("height", "800px")
            .attr("hidden", null);
    }

    // console.log(tableau_share_id);

    if (viz) { // If a viz object exists, delete it.
        viz.dispose();
    }

    var containerDiv = document.getElementById("viz1563725193860");

    if(tableau_share_id.includes("intro")){
        d3.select("#vizIntro")
            .attr("hidden", null);

        d3.select("#vizInsightConatiner")
            .attr("hidden", true);

        d3.select("#viz1563725193860")
            .attr("hidden", true);

        viz = null;
    } else {
        if(tableau_share_id.includes("http")){
            url = tableau_share_id;
        } else {
            url = "https://public.tableau.com/shared/" + tableau_share_id;
        }

        console.log(url);
        viz = new tableau.Viz(containerDiv, url);

        d3.select("#vizInsightConatiner")
            .attr("hidden",null);

        d3.select("#vizInsight")
            .text(summary);
    }
}

d3.csv("./data.csv", function (err, data) {
    if (err) throw err;
    update(data);
});

d3.csv("./background.csv", function (err, data) {
    if (err) throw err;

    updateBackground(data);
});
