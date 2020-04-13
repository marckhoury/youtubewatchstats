function zoom(svg, x, xAxis, margin, width, height) {
    const extent = [[margin.left, margin.top], [width - margin.right, height - margin.top]];

    svg.call(d3.zoom()
       .scaleExtent([1, 20])
       .translateExtent(extent)
       .extent(extent)
       .on("zoom", zoomed));

    function zoomed() {
        x.range([margin.left, width - margin.right].map(d => d3.event.transform.applyX(d)));
        svg.selectAll(".bars rect").attr("x", (d, i) => x(i)).attr("width", x.bandwidth());
        svg.selectAll(".x-axis").call(xAxis);
    }
}
    
function createBarChart(data, svg, margin, width, height, ylabel) {
    var dtf = null;
    if(data.length > 0) {
        if(data[0].date.length == 2) {
            dtf = new Intl.DateTimeFormat('en', { year: '2-digit', month: 'short' });
        } else {
            dtf = new Intl.DateTimeFormat('en', { year: '2-digit', month: 'short', day: '2-digit' });
        }
    }   
    for(let i = 0; i < data.length; i++) {
        data[i].date[1] -= 1; //months are 0-indexed 
        const d = new (Function.prototype.bind.apply(
                       Date, [null].concat(data[i].date)));
        data[i].dateStr = dtf.format(d);
    }     

    var x = d3.scaleBand()
              .domain(d3.range(data.length))
              .range([margin.left, width - margin.right]);
    var xAxis = g => g
                .attr("transform", `translate(0,${height - margin.bottom})`)
                .call(d3.axisBottom(x).tickFormat(i => data[i].dateStr).tickSizeOuter(0))
                .selectAll("text")
                .style("text-anchor", "end")
                .attr("dx", "-.8em")
                .attr("dy", ".15em")
                .attr("transform", "rotate(-65)");

    var y = d3.scaleLinear()
            .domain([0, d3.max(data, d => d.value)]).nice()
            .range([height - margin.bottom, margin.top]);
    var yAxis = g => g
                .attr("transform", `translate(${margin.left},0)`)
                .call(d3.axisLeft(y).ticks(10))
                .call(g => g.append("text")
                        .attr("x", -2*margin.left)
                        .attr("y", 0)
                        .attr("fill", "currentColor")
                        .attr("text-anchor", "start")
                        .style("font-size", "16px")
                        .text(ylabel));

    svg = svg.attr("width", width + margin.left + margin.right)
             .attr("height", height + margin.top + margin.bottom)
             .call(zoom, x, xAxis, margin, width, height)
             .append("g")
             .attr("class", "graph")
             .attr("transform", "translate(" + margin.left + "," + margin.top + ")")
    

    svg.append("g")
       .attr("class", "bars")
       .attr("fill", "steelblue")
       .selectAll("rect")
       .data(data)
       .join("rect")
            .attr("x", (d, i) => x(i))
            .attr("y", d => y(d.value))
            .attr("height", d => y(0) - y(d.value))
            .attr("width", x.bandwidth());    
    
    svg.append("g")
       .attr("class", "x-axis")
       .call(xAxis);

    svg.append("g")
       .attr("class", "y-axis")
       .call(yAxis);
}

function createHistogram(data, svg, margin, width, height) {
    var xMax = d3.max(data) 
    var x = d3.scaleLinear()
              .domain([0, xMax])
              .range([margin.left, width - margin.right]);
    var xAxis = g => g
                .attr("transform", `translate(0,${height - margin.bottom})`)
                .call(g => g.append("text")
                        .attr("x", width / 2 - margin.right)
                        .attr("y", 35)
                        .attr("fill", "currentColor")
                        .attr("text-anchor", "start")
                        .style("font-size", "16px")
                        .text("duration (min)"))
                .call(d3.axisBottom(x).ticks(Math.ceil(xMax)))

    var bins = d3.histogram()
             .domain(x.domain())
             .thresholds(x.ticks(Math.ceil(xMax)))(data)

    var y = d3.scaleLinear()
            .domain([0, d3.max(bins, function(d) { return d.length; })]).nice()
            .range([height - margin.bottom, margin.top]);
    var yAxis = g => g
                .attr("transform", `translate(${margin.left},0)`)
                .call(d3.axisLeft(y).ticks(10))
                .call(g => g.append("text")
                        .attr("x", -2*margin.left)
                        .attr("y", 0)
                        .attr("fill", "currentColor")
                        .attr("text-anchor", "start")
                        .style("font-size", "16px")
                        .text("number of videos"));

    const extent = [[margin.left, margin.top], [width - margin.right, height - margin.top]];

    function zoomedHist() {
        x.range([margin.left, width - margin.right].map(d => d3.event.transform.applyX(d)));
        svg.selectAll(".bars rect").attr("x", (d, i) => x(i)).attr("width", (d, i) => Math.max(0, x(d.x1) - x(d.x0)));
        svg.selectAll(".x-axis").call(xAxis);
    }

    svg = svg.attr("width", width + margin.left + margin.right)
             .attr("height", height + margin.top + margin.bottom)

    svg = svg.call(d3.zoom()
             .scaleExtent([1, 30])
             .translateExtent(extent)
             .extent(extent)
             .on("zoom", zoomedHist));

    svg = svg.append("g")
             .attr("class", "graph")
             .attr("transform", "translate(" + margin.left + "," + margin.top + ")")
   
    svg.append("g")
       .attr("class", "bars")
       .attr("fill", "steelblue")
       .selectAll("rect")
       .data(bins)
       .join("rect")
            .attr("x", d => x(d.x0) + 1)
            .attr("width", d => Math.max(0, x(d.x1) - x(d.x0)))
            .attr("y", d => y(d.length))
            .attr("height", d => y(0) - y(d.length));
     
    svg.append("g")
       .attr("class", "x-axis")
       .call(xAxis);

    svg.append("g")
       .attr("class", "y-axis")
       .call(yAxis);
}
