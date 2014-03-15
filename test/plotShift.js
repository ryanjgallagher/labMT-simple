// make the plot
function plotShift(figure,sortedMag,sortedType,sortedWords) {
    margin = {top: 0, right: 0, bottom: 0, left: 0},
    figwidth = 600 - margin.left - margin.right,
    figheight = 800 - margin.top - margin.bottom,
    width = .775*figwidth,
    height = .775*figheight;

// define the center too, for wordshifting
figcenter = width/2;

// number of words to show
numWords = 35;

// remove an old figure if it exists
figure.select(".canvas").remove();

var canvas = figure.append("svg")
    .attr("width",figwidth)
    .attr("height",figheight)
    .attr("class","canvas")

// create the x and y axis
// scale in x by width of the top word
// could still run into a problem if top magnitudes are similar
// and second word is longer
x = d3.scale.linear()
  .domain([-Math.abs(sortedMag[0]),Math.abs(sortedMag[0])])
  .range([(sortedWords[0].length+3)*9, width-(sortedWords[0].length+3)*9]);

// linear scale function
y =  d3.scale.linear()
    .domain([numWords,1])
    .range([height, 5]); 

// zoom object for the axes
var zoom = d3.behavior.zoom()
    .y(y) //pass linear scale function
    //.translate([10,10])
    .scaleExtent([1,1])
    .on("zoom",zoomed);

// create the axes themselves
var axes = canvas.append("g")
    .attr("transform", "translate(" + (0.125 * figwidth) + "," +
       ((1 - 0.125 - 0.775) * figheight) + ")")
    .attr("width", width)
    .attr("height", height)
    .attr("class", "main")
    .call(zoom);

// create the axes background
axes.append("svg:rect")
    .attr("width", width)
    .attr("height", height)
    .attr("class", "bg")
    .style({'stroke-width':'2','stroke':'rgb(0,0,0)'})
    .attr("fill", "#FCFCFC");

// axes creation functions
var create_xAxis = function() {
    return d3.svg.axis()
    .scale(x)
    .ticks(5)
    .orient("bottom"); }

// axis creation function
var create_yAxis = function() {
   return d3.svg.axis()
    .scale(y) //linear scale function
    .orient("left"); }

// draw the axes
var yAxis = create_yAxis()
    .innerTickSize(6)
    .outerTickSize(0);

axes.append("g")
  .attr("class", "y axis ")
  .attr("transform", "(0,0)")
  .call(yAxis);

var xAxis = create_xAxis()
    .innerTickSize(6)
    .outerTickSize(0);

axes.append("g")
  .attr("class", "x axis ")
  .attr("transform", "translate(0," + (height) + ")")
  .call(xAxis);

d3.selectAll(".tick line").style({'stroke':'black'});

// create the clip boundary
var clip = axes.append("svg:clipPath")
  .attr("id","clip")
  .append("svg:rect")
  .attr("x",0)
  .attr("y",0)
  .attr("width",width)
  .attr("height",height);

// now something else
var unclipped_axes = axes;
 
axes = axes.append("g")
  .attr("clip-path","url(#clip)");

canvas.append("text")
   .text("Word Rank")
   .attr("class","axes-text")
   .attr("x",(figwidth-width)/4)
   .attr("y",figheight/2+30)
   .attr("font-size", "20.0px")
   .attr("fill", "#000000")
   .attr("transform", "rotate(-90.0," + (figwidth-width)/4 + "," + (figheight/2+30) + ")");
   //.attr("style", "text-anchor: middle;");

canvas.append("text")
   .text("Per word average happiness shift")
   .attr("class","axes-text")
   .attr("x",width/2+(figwidth-width)/2)
   .attr("y",3*(figheight-height)/4+height)
   .attr("font-size", "20.0px")
   .attr("fill", "#000000")
   .attr("transform", "rotate(-0.0," + (width/2+(figwidth-width)/2) + "," + (3*(figheight-height)/4+height+10) + ")")
   .attr("style", "text-anchor: middle;");

axes.selectAll(".rect")
   .data(sortedMag)
   .enter()
   .append("rect")
   .attr("fill", function(d,i) { if (sortedType[i] == 2) {return "#4C4CFF";} else if (sortedType[i] == 3) {return "#FFFF4C";} else if (sortedType[i] == 0) {return "#B3B3FF";} else { return "#FFFFB3"; }})
   .attr("class", "rect")
   .attr("x",function(d,i) { 
                             if (d>0) { 
                               return figcenter;
                             } 
                             else { return x(d)} }
                             )
   .attr("y",function(d,i) { return y(i+1); } )
   .style({'opacity':'0.7','stroke-width':'1','stroke':'rgb(0,0,0)'})
   .attr("height",function(d,i) { return 15; } )
   .attr("width",function(d,i) { if (d>0) {return x(d)-figcenter;} else {return figcenter-x(d); } } )
   .on('mouseover', function(d){
        var rectSelection = d3.select(this).style({opacity:'1.0'});
})
   .on('mouseout', function(d){
        var rectSelection = d3.select(this).style({opacity:'0.7'});
});

axes.selectAll(".text")
   .data(sortedMag)
   .enter()
   .append("text")
   //.attr("fill", function(d,i) { if (sortedType[i] == 0 || sortedType[i] == 2) {return "blue";} else { return "yellow"; }})
   .attr("class", "text")
   .style("text-anchor", function(d,i) { if (sortedMag[i] < 0) { return "end";} else { return "start";}})
   .attr("y",function(d,i) { return y(i+1)+11; } )
   .text(function(d,i) { if (sortedType[i] == 0) {tmpStr = "-\u2193";} else if (sortedType[i] == 1) {tmpStr = "\u2193+";}
   else if (sortedType[i] == 2) {tmpStr = "\u2191-";} else {tmpStr = "+\u2191";}
   if (sortedMag[i] < 0) {return tmpStr.concat(sortedWords[i]);} else { return sortedWords[i].concat(tmpStr); } })
   .attr("x",function(d,i) { if (d>0) {return x(d)+2;} else {console.log(sortedWords[i].length); return x(d)-2; } } );

    function zoomed() {
    //console.log(d3.event);
    //console.log(d3.event.translate[1]);
    // d3.event.translate[1] = Math.min(0,d3.event.translate[1])
    axes.selectAll(".rect").attr("transform", "translate(0," + Math.min(0,d3.event.translate[1]) + ")");
    axes.selectAll(".text").attr("transform", "translate(0," + Math.min(0,d3.event.translate[1]) + ")");
    //d3.select(".y.axis").attr("transform", "translate(0," + Math.min(0,d3.event.translate[1]) + ")");
    d3.select(".y.axis").call(yAxis);
    // make the tick lines show up on redraw							    
    d3.selectAll(".tick line").style({'stroke':'black'});
     };

};
