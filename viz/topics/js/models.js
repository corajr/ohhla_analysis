App.navbarItems = [
  Ember.Object.create({"route": "topicGraph", "name": "Topic Model"}),
  Ember.Object.create({"route": "topicSummary", "name": "Summary"}),
  Ember.Object.create({"route": "about", "name": "About"})
];

App.Document = Ember.Object.extend({
  id: "",
  title: "",
  author: "",
  type: "",
  date: new Date(),
  topics: [],
  topWords: [],
});

App.Topic = Ember.Object.extend({
  topWords: [],
  id: -1,
  prevalence: 0.0,

  stdDev: 0.0,
  visible: true,

  prevalencePercent: Ember.computed(function () {
    return (this.get('prevalence')*100).toFixed(2) + "% of corpus";
  }).property('prevalence'),

  relatedTopics: Ember.computed(function () {
    if (!App.topic_topic) return App.topics;
    else {
      var id = this.get('id'), 
          threshold = 0.01,
          topics_idx = argsort(App.topic_topic[id]).slice(0,5),
          topics = App.topics.filter(function (d) { return topics_idx.indexOf(d.id.toString()) != -1 && 
                                                           App.topic_topic[id][d.id] > threshold;});
      topics.sort(function (a,b) { return App.topic_topic[id][b.id] - App.topic_topic[id][a.id];});
      return topics;
      // return App.topics.filter(function (d) { return App.topic_topic[id][d.id] > threshold; });
    }
  }).property('id'),

  documentsForTopic: Ember.computed(function () {
    var topic = this.get('id'),
        docs = App.documents;
    docs.sort(function (a,b) { return b.topics[topic] - a.topics[topic];});
    return docs.slice(0, 100) || [];
  }).property('id', 'App.documents'),

  style: Ember.computed(function() {
    var isSelected = this.get('isSelected'),
        color = isSelected ? this.get('color') : 'lightgray';
    return "color: " + color + ";";
  }).property('color', 'isSelected'),

  styleInvariant: Ember.computed(function() {
    return "color: " + this.get('color') + ";";
  }).property('color'),

  coherence: 0.0,

  isSelected: false,

  color: Ember.computed(function () {
    var topicColors = Ember.get(App, 'topicColors');
    return topicColors(this.get('id'));
  }).property('App.topicColors', 'id'),

  label: function () {
    if (App.topicPhrases) {
      return data['TOPIC_LABELS'][this.id]['phrases'].slice(0,3).join(", ");      
    } else {
      var top = this.topWords.slice(0,3);
      return top.map(function(d){ return d.text || d;}).join(", ");    
    }

  }.property("id")
});