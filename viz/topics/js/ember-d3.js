Ember.D3 = Ember.Namespace.create();

Ember.D3.ChartView = Ember.View.extend({
  tagName: 'svg',
  width: 'auto',
  height: 240,
  margin: {top: 10, right: 10, bottom: 10, left: 10},
  attributeBindings: ['_width:width', 'height'],

  minimumWidth: 100,
  maximumWidth: Ember.computed(function() {
    if (this.get('element')) {
      return this.$().parent().width();
    } else {
      return 0;
    }
  }).property('element').volatile(),

  _width: Ember.computed(function() {
    var width = this.get('width');
    if (width === 'auto') { width = this.get('maximumWidth'); }
    return Math.max(this.get('minimumWidth'), width);
  }).property('width', 'maximumWidth', 'minimumWidth'),

  contentWidth: Ember.computed(function() {
    var margin = this.get('margin');
    return this.get('_width') - margin.left - margin.right;
  }).property('_width', 'margin'),

  contentHeight: Ember.computed(function() {
    var margin = this.get('margin');
    return this.get('height') - margin.top - margin.bottom;
  }).property('height', 'margin'),

  svg: Ember.computed(function() {
    var element = this.get('element');
    return element ? d3.select(element) : null;
  }).property('element'),

  defs: Ember.computed(function() {
    var svg = this.get('svg');

    if (!svg) return;

    var defs = svg.select('defs');
    return defs.empty() ? svg.append('svg:defs') : defs;
  }).property('svg'),

  title: "",
  xAxisLabel: "",
  yAxisLabel: "",

  didInsertElement: function () {
    var svg = this.get('svg'),
        width = this.get('_width'),
        height = this.get('height'),
        margin = this.get('margin'),
        contentWidth = this.get('contentWidth'),
        contentHeight = this.get('contentHeight'),
        title = this.get('title'),
        xAxisLabel = this.get('xAxisLabel'),
        yAxisLabel = this.get('yAxisLabel'),
        vis;

    vis = svg.append("g")
      .attr("width", this.get('contentWidth'))
      .attr("height", this.get('contentHeight'))
      .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    this.set('vis', vis);

    if (title) {
      svg.append("svg:text")
        .attr("x", width/2 )
        .attr("y", 0 + (margin.top / 2))
        .style("text-anchor", "middle")
        .style("font-weight", "bold")
        .text(title);
    }

    if (xAxisLabel) {
      svg.append("svg:text")
        .attr("x", width/2 )
        .attr("y", height - (margin.bottom / 2))
        .style("text-anchor", "middle")
        .text(xAxisLabel);
    }

    if (yAxisLabel) {
      svg.append("svg:text")
        .attr("transform", "rotate(-90)")
        .attr("x", 0 - (height / 2))
        .attr("y", 10) //margin.left / 2)
        .style("text-anchor", "middle")
        .text(yAxisLabel);
    }

    Ember.$(window).on('resize', Ember.$.proxy(this, 'windowDidResize'));
    this.windowDidResize();

    Ember.run.scheduleOnce('afterRender', this, 'renderContent');
  },
  renderContent: function () {
    // implemented in classes
  },
  windowDidResize: function() {
    this.notifyPropertyChange('maximumWidth');
    if (typeof this.onResizeHandler === "function") this.onResizeHandler();
  }  
});