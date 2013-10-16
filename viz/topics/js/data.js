function sumArrays(array1, array2) {
  var len = array1.length;
  while (len--) {
    array1[len] += array2[len];
  }
  return array1;
}

function subtractArrays(array1, array2) {
  var len = array1.length;
  while (len--) {
    array1[len] -= array2[len];
  }
  return array1;
}

function reduceAdd (p, v) {
  return sumArrays(p, v.topics);
}

function reduceSubtract (p, v) {
  return subtractArrays(p, v.topics);
}
function reduceInitial(topics_n) {
  return function () {
    var len = topics_n,
        array = new Array(len);
    while (len--) {
      array[len] = 0.0;
    }
    return array;
  };
}

//https://developer.mozilla.org/en-US/docs/Web/JavaScript/Base64_encoding_and_decoding#Solution_.232_.E2.80.93_rewriting_atob()_and_btoa()_using_TypedArrays_and_UTF-8

function b64ToUint6 (nChr) {

  return nChr > 64 && nChr < 91 ?
      nChr - 65
    : nChr > 96 && nChr < 123 ?
      nChr - 71
    : nChr > 47 && nChr < 58 ?
      nChr + 4
    : nChr === 43 ?
      62
    : nChr === 47 ?
      63
    :
      0;

}

function base64DecToArr (sBase64, nBlocksSize) {

  var
    sB64Enc = sBase64.replace(/[^A-Za-z0-9\+\/]/g, ""), nInLen = sB64Enc.length,
    nOutLen = nBlocksSize ? Math.ceil((nInLen * 3 + 1 >> 2) / nBlocksSize) * nBlocksSize : nInLen * 3 + 1 >> 2, taBytes = new Uint8Array(nOutLen);

  for (var nMod3, nMod4, nUint24 = 0, nOutIdx = 0, nInIdx = 0; nInIdx < nInLen; nInIdx++) {
    nMod4 = nInIdx & 3;
    nUint24 |= b64ToUint6(sB64Enc.charCodeAt(nInIdx)) << 18 - 6 * nMod4;
    if (nMod4 === 3 || nInLen - nInIdx === 1) {
      for (nMod3 = 0; nMod3 < 3 && nOutIdx < nOutLen; nMod3++, nOutIdx++) {
        taBytes[nOutIdx] = nUint24 >>> (16 >>> nMod3 & 24) & 255;
      }
      nUint24 = 0;

    }
  }

  return taBytes;
}

function b64toFloatArray(s) {
    // var raw = window.atob(s),
    //     rawLength = raw.length,
    //     array = new Uint8Array(new ArrayBuffer(rawLength));
    // while (rawLength--) {
    //     array[rawLength] = raw.charCodeAt(rawLength);
    // }
    var array = base64DecToArr(s);
    return new Float32Array(array.buffer);
}

var isoFormatParse = d3.time.format("%Y-%m-%dT%H:%M:%S").parse;

var doc_data = d3.values(data["DOC_METADATA"]),
    len = doc_data.length;

while (len--) {
    var date = doc_data[len].date.trim();
    if (date != "") { // && doc_data[len].topics
      date = isoFormatParse(date);
      doc_data[len].date = date;
      doc_data[len].topics = b64toFloatArray(doc_data[len].topics);
      if (doc_data[len].title.trim() == "") {
        doc_data[len].title = "[untitled]";
      }
      doc_data[len] = App.Document.create(doc_data[len]);
    } else {
      doc_data.splice(len, 1);
    }
}

App.documents = doc_data;

App.topics = [];

App.topic_topic = {};

var topics_n = Object.keys(data['TOPIC_LABELS']).length;
for (var i = 0; i < topics_n; i++) {
  var topic = data['TOPIC_LABELS'][i];
  var topicOccurrence = new Array(App.documents.length);
  for (var k = 0; k < topicOccurrence.length; k++) {
    topicOccurrence[k] = App.documents[k].topics[i];
  }

  App.topics.push(App.Topic.create({
    id: i,
    topWords: topic['words'],
    // relatedTopics: App.topics,
    topicOccurrence: topicOccurrence

  }));
}

d3.sd = function(x) {
  var n = x.length;
  if (n < 1) return NaN;
  if (n === 1) return 0;
  var mean = d3.mean(x),
      i = -1,
      s = 0;
  while (++i < n) {
    var v = x[i] - mean;
    s += v * v;
  }
  return Math.sqrt(s / (n - 1));
};

function label(topicId) {
  return App.topics[topicId].get('label');
}

for (var i = 0; i < topics_n; i++) {
  for (var j = i + 1; j < topics_n; j++) {
    if (!App.topic_topic.hasOwnProperty(i)) {
      App.topic_topic[i] = {};
    }
    var i_vals = App.topics[i].get('topicOccurrence'),
        j_vals = App.topics[j].get('topicOccurrence'),
        i_mean = d3.mean(i_vals),
        j_mean = d3.mean(j_vals),
        i_stdev = d3.sd(i_vals),
        j_stdev = d3.sd(j_vals),
        correlation = 0.0;

    for (var k = 0; k < App.documents.length; k++) {
      correlation += (i_vals[k] - i_mean) * (j_vals[k] - j_mean);
    }
    correlation /= (App.documents.length - 1) * i_stdev * j_stdev;
    App.topic_topic[i][j] = correlation;
  }
}

function correlations() {
  var labeled = {};
  for (var i = 0; i < topics_n; i++) {
    for (var j = i + 1; j < topics_n; j++) {
      try {      
        var i_name = label(i);
        var j_name = label(j);
        labeled[i_name + " x " + j_name] = App.topic_topic[i][j];
      } catch (e) { console.error(e.message)}
    }
  }
  var sorted = argsort(labeled);
  for (var i = 0; i < 15; i++) {
    var key = sorted[i];
    console.log(key + ": " + labeled[key]);
  } 
}

function makeCorrelationGraph(threshold) {
  var graph = {"nodes": [], "links": []};
  var translateIds = {}, idN = 0;
  App.topics.forEach(function (d, i) {
    if (d.get('visible')) {
      var name = d.get('label');
      graph.nodes.push({"id": i, "name": name || ""});
      translateIds[i] = idN;
      idN++;
    }
  });

  for (var i = 0; i < topics_n; i++) {
    for (var j = i + 1; j < topics_n; j++) {
      if (App.topics[i].get('visible') && App.topics[j].get('visible')) {
        if (App.topic_topic[i][j] > threshold) {
          graph.links.push({"source": translateIds[i], "target": translateIds[j], "value": App.topic_topic[i][j]});
        }
      }
    }
  }
  return graph;
}

function getDoc(itemID) {
  return App.documents.find(function (d) { return d.itemID == itemID; });
}