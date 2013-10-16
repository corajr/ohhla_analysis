App.TopicGraphParentView = Ember.D3.ChartView.extend({
  width: 'auto',
  height: 450,
  minimumWidth: 600,
  margin: {top: 20, right: 0, bottom: 30, left: 45},

  yAxisLabel: "% of Corpus",
  graphType: Ember.computed(function () {
    return this.get('controller.graphType');
  }).property('controller.graphType'),
  intervalType: "year", // other options: "month" or "day"
  interval: Ember.computed(function() {
    return d3.time[this.get('intervalType')];
  }).property('intervalType'),

  timeFormat: Ember.computed(function() {
    var intervalType = this.get('intervalType'),
        format;
    if (intervalType == "year") {
      format = d3.time.format("%Y");
    } else if (intervalType == "month") {
      format = d3.time.format("%Y-%m");      
    } else {
      format = d3.time.format("%Y-%m");
    }
    return format;
  }).property('intervalType', 'interval'),

  timeTickFormat: Ember.computed(function() {
    var timeFormat = this.get('timeFormat');
    return function(d){ return timeFormat(new Date(d)); };
  }).property('timeFormat'),

  yDomain: Ember.computed(function () {
    var graphType = this.get('graphType');
    if (graphType == 'stacked')
      return [0, 1];
    else if (graphType == 'stream')
      return [0, d3.max(this.get('streamData'), 
        function(d) { return d3.max(d, function(d) { return d.y0 + d.y; }); })];
    else if (graphType == 'line')
      return [-3, 3];
  }).property('graphType', 'streamData'),

  xScale: Ember.computed(function () {
    return d3.time.scale()
      .range([0, this.get('contentWidth')]);
  }).property('interval', 'contentWidth'),

  yScale: Ember.computed(function () {
    var yDomain = this.get('yDomain');
    return d3.scale.linear()
      .domain(yDomain)
      .range([this.get('contentHeight'), 0]);
  }).property('contentHeight', 'yDomain'),

  xAxis: Ember.computed(function() {
    var height = this.get('contentHeight');
    return d3.svg.axis()
              .scale(this.get('xScale'))
              .orient("bottom")
              .tickFormat(this.get('timeTickFormat'))
              .tickSize(-height)
              .tickSubdivide(this.get('intervalType') == "year" ? 4 : 1)
  }).property('timeTickFormat', 'intervalType', 'xScale'),

  yAxis: Ember.computed(function() {
    var width = this.get('contentWidth'),
        graphType = this.get('graphType');
    if (graphType == 'stacked') {
      return d3.svg.axis()
        .scale(this.get('yScale'))
        .orient("left")
        .tickSize(-width)
        .tickFormat(d3.format("%"))
        // .tickSubdivide(1)
        .ticks(5);
    } else if (graphType == 'line') {
      return d3.svg.axis()
        .scale(this.get('yScale'))
        .orient("left")
        .tickSize(-width)
        // .tickSubdivide(1)
        .ticks(5);
    } else { // give a blank axis
      return d3.svg.axis()
        .scale();
    }
  }).property('yScale', 'contentWidth', 'offset'),


  gradientScale: Ember.computed(function () {
    var docCounts = this.get('docCounts');
    console.log(d3.max(docCounts));
    return d3.scale.pow()
      .exponent(0.1)
      .clamp(true)
      .domain([0, docCounts ? d3.max(docCounts) : 0])
      .range([1,0]);
  }).property('docCounts'),

  createGroups: function () {
    var vis = this.get('vis'),
        defs = this.get('defs'),
        width = this.get('contentWidth'),
        height = this.get('contentHeight');
               
    vis.selectAll("*").remove();
    if (vis.selectAll(".group").empty()) {
      defs.append("clipPath")
       .attr("id","plot-region")
       .append("rect")
       .attr("width", width)
       .attr("height", height);
      this.set('graphGroup', vis.append("g")
        .attr("class", "graph group")
        .attr("clip-path", "url(#plot-region)"));
      this.set('gradientGroup', vis.append("g").attr("class", "gradient group"));
      this.set('axesGroup', vis.append("g").attr("class", "axes group"));
    }
  },

  stack: Ember.computed(function () {
    return d3.layout.stack()
      .offset(this.get('offset'))
      .order(this.get('order'));
  }).property("offset", "order"),

  timeDomain: Ember.computed(function () {
    var interval = this.get('interval'),
        docsByTime = this.get('docsByTime'),
        overallTimeDomain = App.get('timeDomain');
    if (overallTimeDomain) {
      docsByTime.filterRange(overallTimeDomain);
      return overallTimeDomain;
    } else if (docsByTime) {
      var first_doc = docsByTime.bottom(1)[0],
          last_doc = docsByTime.top(1)[0];
      return [interval.floor(first_doc.date), interval.ceil(last_doc.date)];
    } else {
      return [new Date(), new Date()];
    }
  }).property('interval', 'docsByTime', 'App.timeDomain'),

  interpolateType: 'monotone',
  offset: Ember.computed(function () {
    var graphType = this.get('graphType');
    return graphType == 'stacked' ? 'zero' : 'wiggle';
  }).property('graphType'),

  order: 'default',

  area: Ember.computed(function () {
    var x = this.get('xScale'),
        y = this.get('yScale'),
        interpolateType = this.get('interpolateType');

    return d3.svg.area()
      .interpolate(interpolateType)
      .x(function(d) { return x(d.x); })
      .y0(function(d) { return y(d.y0); })
      .y1(function(d) { return y(d.y0 + d.y); });
  }).property('xScale', 'yScale', 'interpolateType'),

  line: Ember.computed(function () {
    var x = this.get('xScale'),
        y = this.get('yScale'),
        interpolateType = this.get('interpolateType');
    return d3.svg.line()
      .interpolate(interpolateType)
      .x(function(d) { return x(d.x); })
      .y(function(d) { return y(d.y); });
  }).property('xScale', 'yScale', 'interpolateType'),


  docsByTime: function() {
    return this.get('controller.documents.docsByTime');
  }.property('controller.documents.docsByTime'),

  topicIntervals: Ember.computed(function () {
    var interval = this.get('interval'),
        docsByTime = this.get('docsByTime'),
        topics_n = this.get('controller.topics.n'),
        docGroupsByInterval = docsByTime.group(function (date) { return interval.floor(date); });
    return docGroupsByInterval.reduce(reduceAdd, reduceSubtract, reduceInitial(topics_n)).all();
  }).property('interval', 'docsByTime', 'controller.topics.n'),

  topicMeans: Ember.computed(function () {
    return this.get('controller.topics.prevalences');
  }).property('topicIntervals'),

  topicStdDevs: Ember.computed(function () {
    var topicIntervals = this.get('topicIntervals'),
        topics_n = this.get('controller.topics.n'),
        topicMeans = this.get('topicMeans');

    var topicVariances = topicIntervals.reduce(function (a,b) {
      return sumArrays(a, subtractArrays(b.value, topicMeans).map(function(d){ return d*d;}));
    }, reduceInitial(topics_n)()).map(function(d) { return d / (topicIntervals.length - 1)});
    var topicStdDevs = topicVariances.map(function(d) { return Math.sqrt(d);});

    this.get('controller.topics').set('stdDevs', topicStdDevs);
    this.get('controller.topics.content').forEach(function (d,i) { 
      d.set('stdDev', topicStdDevs[i]);
    });

    return topicStdDevs;
  }).property('topicIntervals'),

  lineData: Ember.computed(function () {
    var intervals = this.get('topicIntervals'),
        topicStdDevs = this.get('topicStdDevs'),
        topicMeans = this.get('topicMeans'),  
        docCounts = this.get('docCounts'),
        topics = this.get('controller.topics'),
        topics_n = topics.get('n'),
        activeTopics = this.get('activeTopics'),
        smooth = this.get('smooth').bind(this);

    if (!activeTopics || activeTopics.length == 0) {
      return [];
    } else {
      var all_layers = new Array(topics_n),
          len = topics_n;
      while (len--) {
        all_layers[len] = intervals.map(
          function (d,i) { var y = 0.0;
                           if (docCounts[i] != 0 && topicStdDevs[len] != 0) {
                             y = d.value[len] / docCounts[i];
                             y -= topicMeans[len];
                             y /= topicStdDevs[len];
                           }
                           return { x: d.key, topic: len, y: y }; 
        });
      }

      all_layers = smooth(all_layers);
      return all_layers.filter(function (_, i) { return activeTopics.indexOf(i) !== -1; });
    }    
  }).property('interval', 'controller.topics', 'controller.topics.selectedIDs', 'topicIntervals', 'docCounts', 'topicStdDevs'),

  docCounts: Ember.computed(function () {
    var interval = this.get('interval'),
        docsByTime = this.get('docsByTime'),
        groupByInterval = docsByTime.group(function (date) { return interval.floor(date); }),
        docCounts = groupByInterval.reduceCount().all().map(function (d) { return d.value;});
    App.set('docCounts', docCounts);
    return docCounts;
  }).property('interval', 'docsByTime', 'topicIntervals'),

  activeTopics: Ember.computed(function () {
    return this.get('controller.topics.selectedIDs');
  }).property('controller.topics.selectedIDs'),

  smoothParams: {"type": "mean", "window": 3},
  smooth: function(layers) {
    var smoothParams = this.get("smoothParams"),
        type = smoothParams["type"],
        windowSize = smoothParams["window"];
    if (type) {
      for (var i = 0; i < layers.length; i++) {
        var d = layers[i],
            smoothed = [];
        for (var j = 0, n = d.length; j < n; j++) {
          var sample = [];
          for (var k = -windowSize; k <= windowSize; k++) {
            if (j+k >= 0 && j+k < n) {
              sample.push(d[j + k].y);        
            } else {
              sample.push(d[j].y);
            }
          }
          if (type == "median") {
            smoothed.push(d3.median(sample));            
          } else if (type == "mean") {
            smoothed.push(d3.mean(sample));            
          }
        }
        for (var j = 0, n = d.length; j < n; j++) {
          d[j].y = smoothed[j];
        }
      }    
    }
    return layers;
  },

  layers: Ember.computed(function () {
    var intervals = this.get('topicIntervals'),
        stdDevs = this.get('topicStdDevs'),
        docCounts = this.get('docCounts'),
        topics = this.get('controller.topics'),
        topics_n = topics.get('n'),
        activeTopics = this.get('activeTopics'),
        smooth = this.get('smooth').bind(this);

    if (!activeTopics || activeTopics.length == 0) {
      return [];
    } else {
      var all_layers = new Array(topics_n),
          len = topics_n;
      while (len--) {
        all_layers[len] = intervals.map(
          function (d,i) { var y = docCounts[i] != 0 ? d.value[len] / docCounts[i] : 0 ;
                           return { x: d.key, topic: len, y: y }; 
        });
      }

      all_layers = smooth(all_layers);
      return all_layers.filter(function (_, i) { return activeTopics.indexOf(i) !== -1; });
    }
  }).property('interval', 'controller.topics', 'controller.topics.selectedIDs', 'topicIntervals', 'docCounts'),

  streamData: Ember.computed(function () {
    var layers = this.get('layers'),
        stack = this.get('stack');
    // console.log(layers);
    return layers.length > 0 ? stack(layers) : [];
  }).property('layers'),

  updateAxes: function() {
    var xScale = this.get('xScale'),
        yScale = this.get('yScale'),
        axesGroup = this.get('axesGroup'),
        height = this.get('contentHeight');

    if (!axesGroup) return;

    axesGroup.selectAll(".axis").remove();

    axesGroup.append("svg:g")
      .attr("class", "x axis")
      .attr("transform", "translate(0," + height + ")")
      .call(this.get('xAxis'));

    axesGroup.append("svg:g")
      .attr("class", "y axis")
      .call(this.get('yAxis'));
  }.observes('yDomain'),


  highlightTopic: function (topic) {
    var graphGroup = this.get('graphGroup'),
        activeTopics = this.get('activeTopics'),
        filled = true,
        defaultOpacity = 1.0;

    if (activeTopics.indexOf(topic) == -1) return;
    App.set('hoverTopic', topic);
    // legend.style("fill-opacity", function (d) { return (d.topic == topic) ? 1.0 : (d.active ? 0.7 : 0.3);})
    // for (i in graph) {
    var series = graphGroup.selectAll("path");
    series.transition().style(filled ? "fill-opacity": "stroke-opacity", function (d) {
        return (d[0].topic != topic) ? defaultOpacity * 0.3 : defaultOpacity;
    });
  },
  unhighlightTopic: function() {
    var graphGroup = this.get('graphGroup'),
        defaultOpacity = 1.0,
        filled = true;

    App.set('hoverTopic', null);
    // return;
    // legend.style("fill-opacity", function (d) { return (d.active) ? 1.0 : 0.3;})
    // for (i in graph) {
      var series = graphGroup.selectAll("path"); //+ i.toString());
      series.transition().style(filled ? "fill-opacity" : "stroke-opacity", 1.0);
    //   if (categorical) {
    //     var bars = graphGroup.selectAll("g.bar.graph" + i.toString());
    //     bars.transition().style("fill-opacity", graph[i].defaultOpacity);
    //   }
    // }
  },
  getDocsForInterval: function(d, i) {
    var xScale = this.get('xScale'),
        graphGroup = this.get('graphGroup'),
        mouseX = d3.mouse(graphGroup[0][0])[0],
        time = xScale.invert(mouseX),
        interval = this.get('interval'),
        docsByTime = this.get('docsByTime'),
        timeDomain = this.get('timeDomain'),
        topic = d[0].topic;

    var docs = docsByTime
      .filterRange([interval.floor(time), interval.ceil(time)])
      .top(100);

    docsByTime.filterRange(timeDomain);

    docs.sort(function (a,b) { return b.topics[topic] - a.topics[topic];});
    App.showDocs(docs, topic);
  },
  maskClouds: {},
  updateGraph: function () {
    var color = Ember.get(App, 'topicColors'),
        area = this.get('area'),
        line = this.get('line'),
        graphGroup = this.get('graphGroup'),
        streamData = this.get('streamData'),
        lineData = this.get('lineData'),
        graphType = this.get('graphType'),
        maskClouds = this.get('maskClouds'),
        defs = this.get('defs'),
        width = this.get('contentWidth'),
        height = this.get('contentHeight'),
        highlightTopic = this.get('highlightTopic').bind(this),
        unhighlightTopic = this.get('unhighlightTopic').bind(this),
        getDocsForInterval = this.get('getDocsForInterval').bind(this);

    if (!graphGroup) return;
    graphGroup.selectAll(".graph").remove();

    if (graphType == 'stream' || graphType == 'stacked') {
      var graphSelection = graphGroup.append("svg:g")
        .attr("class", "graph")
        .selectAll("path")
          .data(streamData);      

      graphSelection.enter().append("svg:path")
          .attr("class", function (d) { return "topic" + d[0].topic;})
          .attr("d", function(d) { return area(d);})
          .style("fill", function (d,i) { return color(d[0].topic);})
          .on("mouseover", function (d) { highlightTopic(d[0].topic);})
          .on("mouseout", unhighlightTopic)
          .on("click", getDocsForInterval);

      defs.selectAll("clipPath.topic").remove();
      defs.selectAll("clipPath.topic")
        .data(streamData)
        .enter().append("svg:clipPath")
          .attr("id", function (d) { return "clipTopic" + d[0].topic;})
          .attr("class", "topic")
        .append("svg:path")
          .attr("d", function(d) { return area(d);});

      d3.selectAll(".cloud").remove();
      graphSelection.each(function (d) {
        var topic = d[0].topic;
        var values = App.topics[topic].topWords.map(function (d) { return d.prob;});
        var cloudFontSize = d3.scale.linear().clamp(true).domain(d3.extent(values)).range([10,36]);

        maskClouds[topic] = new MaskCloud();
        maskClouds[topic]
          .size([width,height])
          .words(App.topics[topic].topWords.filter(function (_,i) { return i < 10;})
              .map(function(e) {
                return {text: e.text, size: cloudFontSize(e.prob)};}
              )
            )
          .svg("<path d='"+ area(d) + "'></path>")
          .clip("#clipTopic"+topic)
          .parent(graphGroup.select("g.graph")) //path.topic" + i.toString()))
          .color(color(topic))
          .start();
      });
    } else if (graphType == 'line') {
      var graphSelection = graphGroup.append("svg:g")
        .attr("class", "graph")
        .selectAll("path")
          .data(lineData);      

      graphSelection.enter().append("svg:path")
          .attr("class", function (d) { return "topic" + d[0].topic;})
          .attr("d", function(d) { return line(d);})
          .style("fill", function (d,i) { return color(d[0].topic);})
          .on("mouseover", function (d) { highlightTopic(d[0].topic);})
          .on("mouseout", unhighlightTopic)
          .on("click", getDocsForInterval);      
    }
  }.observes('layers'),

  gradientDef: Ember.computed(function() {
    var gradientScale = this.get('gradientScale'),
        docCounts = this.get('docCounts'),
        defs = this.get('defs'),
        gradientDef;

    if (!defs || !docCounts) return;
    gradientDef = defs.selectAll("#linearGradientDensity");

    gradientDef.data([docCounts]).enter().append("svg:linearGradient")
      .attr("id", "linearGradientDensity")
      .attr("x1", "0%")
      .attr("y1", "0%")
      .attr("x2", "100%")
      .attr("y2", "0%")
    .selectAll("stop").data(function (d) { return d; })
      .enter().append("svg:stop")
        .attr("offset", function (d, i) { return ((100.0 * i) / docCounts.length) + "%"; })
        .attr("stop-color", "#fff")
        .attr("stop-opacity", function (d) { return gradientScale(d); });

    return gradientDef;
  }).property('defs', 'gradientScale'),

  updateGradient: function () {
    var width = this.get('contentWidth'),
        height = this.get('contentHeight'),
        gradientDef = this.get('gradientDef'),
        gradientGroup = this.get('gradientGroup');

    if (!gradientGroup) return;

    gradientGroup.append("rect")
      .attr("id", "density")
      .style("fill", "url(#linearGradientDensity)")
      .style("pointer-events", "none")
      .attr("width", width)
      .attr("height", height);
  }.observes('gradientDef'),

  renderContent: function () {
    this.createGroups();
    var xScale = this.get('xScale'),
        yScale = this.get('yScale');

    xScale.domain(this.get('timeDomain'));
    yScale.domain(this.get('yDomain'));

    this.updateAxes();
    this.updateGraph();
    this.updateGradient();
  },
  onResizeHandler: function () {
    this.renderContent();
  }
});

App.TopicGraphStreamView = App.TopicGraphParentView.extend({});
App.TopicGraphStackedView = App.TopicGraphParentView.extend({});
App.TopicGraphLineView = App.TopicGraphParentView.extend({});

App.set('cloud', Ember.D3.WordCloudView.create({
  contentBinding: "App.hoverTopicWords",
  colorBinding: "App.hoverTopicColor"
}));
