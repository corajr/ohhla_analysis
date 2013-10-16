App.ApplicationController = Ember.Controller.extend({
  needs: ['documents', 'topics'],

  topicPrevalence: function () {
    return this.get('controllers.topics.prevalences');
  }.property('controllers.topics.prevalences'),

  topicColors: Ember.computed(function () {
    var topic_ids = App.topics.getEach('id'),
        topicPrevalence = this.get('topicPrevalence');
    topic_ids.sort(function (a,b) { return topicPrevalence[b] - topicPrevalence[a];});
    return d3.scale.category20().domain(topic_ids);
  }).property('App.topics', 'topicPrevalence'),
  updatePath: function() {
    App.set("currentPath", this.currentPath);
    // window.document.title = this.controllerFor(this.currentPath).get('title');
  }.observes('currentPath'),
});

App.DocumentsController = Ember.ArrayController.extend(EmberCrossfilter, {
  content: App.documents,
  ascending: {
    'date': true,
    'title': true,
    'author': true,
    'type': true
  },
  sortBy: function (type) {
    var asc = this.get('ascending');
    asc[type] = !asc[type];
    this.set('ascending', asc);
    console.log(type, asc[type]);
    this.sortContent(type, asc[type]);
  },
  filterMap: {
    minDate: { property: 'date', dimension: 'date', method: 'filterRangeMin'},
    maxDate: { property: 'date', dimension: 'date', method: 'filterRangeMax'},
  },
  sort: { sortProperty: 'date', isAscending: true }, 
  docsFilter: function() {
    return this.get('_crossfilter');
  }.property('content'),
  docsByTime: function() {
    return this.get('docsFilter').dimension(function (d) { return d.date;});
  }.property('docsFilter')
});

App.DocumentsTableController = Ember.Table.TableController.extend({
  hasHeader: true,
  hasFooter: false,
  numFixedColumns: 0,
  numRows: 0,
  rowHeight: 30,
  fluidTable: true,
  columns: Ember.computed(function () {
    var columns, dateColumn, titleColumn, activePercentColumn, columnNames, columnSizes;
    dateColumn = Ember.Table.ColumnDefinition.create({
      columnWidth: "15%",
      headerCellName: "Date",
      getCellContent: function (row) {
        return dateToStr(row['date']);
      }
    });
    activePercentColumn = Ember.Table.ColumnDefinition.create({
      columnWidth: "15%",
      headerCellNameBinding: "App.clickedTopicLabel",
      getCellContent: function (row) {
        var topic = App.get('clickedTopic');
        if (topic)
          return ratioToStr(row['topics'][topic]);
        else
          return "";
      }
    });
    titleColumn = Ember.Table.ColumnDefinition.create({
      columnWidth: "70%",
      headerCellName: "Title",
      getCellContent: function (row) {
        return localItemLink(row['title'], row['itemID']);
      }
    });

    columnNames = [];
    // columnNames = ['author'];
    // columnSizes = ["20%"];
    // columnNames = ['author', 'type'];
    // columnSizes = ["20%", "10%"];
    columns = columnNames.map(function(key, index) {
      var name;
      name = key.charAt(0).toUpperCase() + key.slice(1);
      return Ember.Table.ColumnDefinition.create({
        columnWidth: columnSizes[index],
        headerCellName: name,
        getCellContent: function(row) {
          return row[key];
        }
      });
    });
    columns.unshift(dateColumn, titleColumn);
    columns.push(activePercentColumn);
    return columns;
  }).property()
});

App.documentsTable = App.DocumentsTableController.create({
  contentBinding: "App.selectedDocs",
});

App.TopicsController = Ember.ArrayController.extend({
  needs: ['documents'],
  content: App.topics,
  documents: null,
  documentsBinding: "controllers.documents",
  init: function () {
    this._super();
    var prevalences = this.get('prevalences');
    this.get('content').forEach(function (d, i) {
      d.set('prevalence', prevalences[i]);
    });
  },
  n: function() {
    var documents = this.get('documents');
    return documents.get('content')[0].topics.length;
  }.property('documents.content'),

  prevalences: function () {
    var documents = this.get('documents'),
        docsFilter = documents.get('docsFilter'),
        prevalences = docsFilter.groupAll()
          .reduce(reduceAdd, reduceSubtract,reduceInitial(this.get('n')))
          .value()
          .map(function (d) { return d / docsFilter.size(); });

    return prevalences;
  }.property('documents.docsFilter'),

  deselectAll: function () {
    this.get('content').setEach('isSelected', false);
  },

  select: function (ids) {
    var topics = this.get('content');
    topics.setEach('isSelected', false);
    ids.forEach(function (id) {
      console.log(id);
      if (id < topics.length - 1)
        topics[id].set('isSelected', true);
    });
  },
  selected: Ember.computed(function() {
    return this.get('content').filterProperty('isSelected');
  }).property('content.@each.isSelected'),

  selectedIDs: Ember.computed(function() {
    return this.get('selected').getEach('id');
  }).property('content.@each.isSelected'),

  sortProperties: ['isSelected', 'prevalence'],
  sortAscending: false
});


App.TopicGraphController = Ember.ObjectController.extend({
  needs: ['documents', 'topics'],
  graphType: "stacked",
  graphTypes: [
    Ember.Object.create({id: 'stacked', label: 'Stacked Area'}),
    Ember.Object.create({id: 'stream', label: 'Streamgraph'}),
    Ember.Object.create({id: 'line', label: 'Line Graph'})
  ],
  documents: null,
  topics: null,
  documentsBinding: "controllers.documents",
  topicsBinding: "controllers.topics",
  sort: function (type) {
    console.log(type);
    var topics = this.get('topics');
    topics.set('sortProperties', ['isSelected', type]);      
  },
  graphTypeName: Ember.computed(function () {
    var graphType = this.get('graphType'),
        name = "";
    if (graphType == "stacked") name = "Stacked Area";
    else if (graphType == "stream") name = "Streamgraph";
    else if (graphType == "line") name = "Line Graph";
    return name;
  }).property('graphType')
});

App.TopicGraphStreamController = App.TopicGraphController.extend({
  graphType: "stream"
});

App.TopicGraphStackedController = App.TopicGraphController.extend({
  graphType: "stacked"
});

App.TopicGraphLineController = App.TopicGraphController.extend({
  graphType: "line"
});

App.TopicSummaryController = Ember.ObjectController.extend({
  needs: ['documents', 'topics'],
  documents: null,
  topics: null,
  documentsBinding: "controllers.documents",
  topicsBinding: "controllers.topics",
  threshold: 0.1,
  content: Ember.computed(function () {
    console.log("running ");
    var threshold = this.get('threshold');
    var graph = makeCorrelationGraph(threshold);
    return graph;
  }).property('threshold', 'topics.@each.visible')  
});