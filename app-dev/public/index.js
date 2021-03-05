// import d3 from "d3";

// var width = 960;
// var height = 1160;

// var projection = d3.geoPath()
//     .center([0, 55.4])
//     .rotate([4.4, 0])
//     .parallels([50, 60])
//     .scale(6000)
//     .translate([width / 2, height / 2]);

const width = window.innerWidth * 0.5;
const height = window.innerHeight * 0.5;

var usaSvg = d3.select("#usa-container")
	.append("svg")
	.attr("width", width)
	.attr("height", height)
	.attr("id", "usa-map");

var stateSvg = d3.select("#state-container")
	.append("svg")
	.attr("width", width)
	.attr("height", height)
	.attr("id", "state-map");

const usaTopo = d3.json("data/USA.topo.json");
usaTopo.then((usa) => {
	var states = topojson.feature(usa, usa.objects.data);
	var projCountry = d3.geoIdentity().fitSize([width, height], states)
	var statePath = d3.geoPath(projCountry);

	usaSvg.selectAll("path")
		.data(states.features)
		.enter()
		.append("path")
		.attr("d", statePath)
		.attr("class", "state")
		.attr("fill", "black")
		.attr("stroke", "red")
		.attr("id", (d) => d.properties.id)
		.on("mouseover", mouseOverHandler)
		.on("mouseout", mouseOutHandler)
		.on("click", clickHandler);
});

function mouseOverHandler() {
	d3.select(this).attr("fill", "red");
}

function mouseOutHandler() {
	d3.select(this).attr("fill", "black");
}

function clickHandler(d) {
	var stateID = d.properties.id;
	var stateTopo = d3.json(`data/${stateID}.topo.json`);
	stateTopo.then((state) => {
		var cds = topojson.feature(state, state.objects.data);
		var projState = d3.geoIdentity().fitSize([width*0.5, height*0.5], cds).reflectY(true);
		var cdPath = d3.geoPath(projState);
		var centroid = cdPath.centroid(cds);
		var x = width / 2 - centroid[0];
		var y = height / 2 - centroid[1];

		d3.select("#cds").remove();

		var g = d3.select("#state-map")
			.append("g")
			.attr("id", "cds");

		g.selectAll("path")
			.data(cds.features)
			.enter()
			.append("path")
			.attr("d", cdPath)
			.attr("transform", `translate(${x}, ${y})`)
			.attr("class", "congressional-district")
			.attr("fill", "red")
			.attr("stroke", "black")
			.attr("id", (d) => d.properties.cd + stateID);

	});
}
