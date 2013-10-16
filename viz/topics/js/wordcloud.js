Ember.D3.WordCloudView = Ember.D3.ChartView.extend({
  width: 'auto',
  height: 150,
  fontSizePixels: [10,48],
  fontSize: Ember.computed(function() {
    return d3.scale.log().range(this.get('fontSizePixels'));
  }).property('content', 'fontSizePixels'),
  color: "#000",
  draw: Ember.computed(function () {
    var width = this.get('contentWidth'),
        height = this.get('contentHeight'),
        vis = this.get('vis'),
        me = this;
    return function(words) {
      var colorHash = me.get('colorHash'), 
          labelHash = me.get('labelHash');
      vis.selectAll("g").remove();
      var drawn = vis.append("g")
        .attr("transform", "translate(" + width/2 + "," + height/2 + ")")
        .selectAll("text")
          .data(words)
        .enter().append("g")
          .attr("transform", function(d) {
            return "translate(" + [d.x, d.y] +")rotate(" + d.rotate + ")";
          });

      drawn
        .append("text")
        .style("font-size", function(d) { return d.size + "px"; })
        .attr("text-anchor", "middle")
        .style("fill", function (d) { return colorHash ? colorHash[d.text] : "#000"; })
        .text(function(d) { return d.text; });

      drawn
        .append("svg:title").text(function (d) { return labelHash[d.text];});
    };
  }).property('vis', 'color', 'colorHash', 'labelHash'),
  renderContent: function () {
    var word_data = this.get('content'),
        width = this.get('contentWidth'),
        height = this.get('contentHeight'),
        fontSize = this.get('fontSize'),
        color = this.get('color'),
        draw = this.get('draw');

    if (!word_data) return;
    var values = [], colors = {}, labels = {};
    word_data.forEach(function (d) {
      d.value = +d.prob;
      values.push(d.value);
      colors[d.text] = typeof color === "function" ? color(d.topic) : color;
      labels[d.text] = d.topic ? App.topics[d.topic].get('label') : d.value;
    });
    this.set('colorHash', colors);
    this.set('labelHash', labels);

    fontSize.domain(d3.extent(values));

    d3.layout.cloud().size([width, height])
      .words(word_data)
      .timeInterval(10)
      .rotate(0) //function() { return ~~(Math.random() * 2) * 90; })
      .fontSize(function(d) { return fontSize(+d.value); })
      .on("end", draw)
      .start();
  }.observes('content')
});