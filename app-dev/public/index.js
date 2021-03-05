const width = window.innerWidth * 0.45;
const height = window.innerHeight * 0.45;

var usaSvg = d3.select("#usa-container")
	.append("svg")
	.attr("width", width)
	.attr("height", height)
	.attr("id", "usa-map")
	.attr("class", "map-svg");

var stateSvg = d3.select("#state-container")
	.append("svg")
	.attr("width", width)
	.attr("height", height)
	.attr("id", "state-map")
	.attr("class", "map-svg");

var borderRect = d3.selectAll(".map-svg")
	// .attr("viewBox", `0 0 ${width*1.2} ${height*1.2}`)
	.append("rect")
	.attr("width", "100%")
	.attr("height", "100%")
	.attr("class", "border")
	.attr("fill", "none")
	.attr("stroke", "black")
	.attr("border", 5);

const nationColor = d3.scaleOrdinal().domain([0, 51]).range([
	"#855C75", "#D9AF6B", "#AF6458", "#736F4C", "#526A83", "#625377",
	"#68855C", "#9C9C5E", "#A06177", "#8C785D", "#467378", "#7C7C7C"
]);

const usaTopo = d3.json("data/USA.topo.json");
usaTopo.then((usa) => {
	var states = topojson.feature(usa, usa.objects.data);
	var projCountry = d3.geoIdentity().fitSize([width*0.9, height*0.9], states)
	var statePath = d3.geoPath(projCountry);

	usaSvg.selectAll("path")
		.data(states.features)
		.enter()
		.append("path")
		.attr("d", statePath)
		.attr("class", "state")
		.attr("fill", (d, i) => nationColor(i))
		.attr("stroke", "black")
		.attr("id", (d) => d.properties.id)
		.on("mouseover", mouseOverHandler)
		.on("mouseout", mouseOutHandler)
		.on("click", clickHandler);
});

function mouseOverHandler() {
	d3.select(this).attr("fill", "black");
	// d3.select(this).
}

function mouseOutHandler(d, i) {
	d3.select(this).attr("fill", nationColor(i));
};

function clickHandler(d) {
	var stateID = d.properties.id;
	var stateTopo = d3.json(`data/${stateID}.topo.json`);
	stateTopo.then((state) => {
		var cds = topojson.feature(state, state.objects.data);
		var projState = d3.geoIdentity().fitSize([width*0.9, height*0.9], cds).reflectY(true);
		var cdPath = d3.geoPath(projState);
		var centroid = cdPath.centroid(cds);
		var x = width / 2 - centroid[0];
		var y = height / 2 - centroid[1];
		const stateColor = d3.scaleOrdinal().domain(cds).range([
			"#88CCEE", "#CC6677", "#DDCC77", "#117733", "#332288", "#AA4499",
			"#44AA99", "#999933", "#882255", "#661100", "#6699CC", "#888888"
		]);

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
			.attr("fill", (d, i) => stateColor(i))
			.attr("stroke", "black")
			.attr("id", (d) => d.properties.cd + stateID);

	});
}
