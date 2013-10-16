function drawPixelArray(pix, width, height) {
  var pixCanvas = document.createElement("canvas");
  var ratio = Math.sqrt(pixCanvas.getContext("2d").getImageData(0, 0, 1, 1).data.length >> 2);
  var w = width / ratio,
      w32 = width >> 5,
      h = height / ratio;
  pixCanvas.width = w;
  pixCanvas.height = h;
  // pixCanvas.style.top = 0;
  // pixCanvas.style.position = "absolute";

  var c = pixCanvas.getContext("2d");
  var imageData = c.createImageData(w, h);

  var pixels = imageData.data;

  for (var j = 0; j < height; j++) {
    for (var i = 0; i < width; i++) {
      var k = w32 * j + (i >> 5),
          m = pix[k] & 1 << (31 - (i % 32)),
          idx = (j * width + i) << 2;

        if (m | 0) {
          pixels[idx] = 0x00;
          pixels[idx+1] = 0x00;
          pixels[idx+2] = 0x00;
          pixels[idx+3] = 0x66;          
        }
      }
    }    
  c.putImageData(imageData, 0, 0);
  document.body.appendChild(pixCanvas);
  return pixCanvas;
}

function MaskCloud() {
  var size = [256, 256],
      cloudW = size[0],
      cloudH = size[1],
      valid_blocks = [],
      words = [],
      parent = d3.select("g.graph"),
      cloud,
      me = this,
      canvas = null,
      svg,
      clip,
      maxForParams = 0.0,
      bestArrangementSoFar = null,
      attempts = 0;

  this.size = function (x) {
    if (!arguments.length) return size;
    size = [+x[0], +x[1]];
    cloudW = size[0];
    cloudH = size[1];
    return this;
  };

  this.parent = function (x) {
    if (!arguments.length) return parent;
    parent = x;
    return this;
  };
  this.color = function (x) {
    if (!arguments.length) return color;
    color = x;
    return this;
  };

  this.clip = function (x) {
    if (!arguments.length) return clip;
    clip = x;
    return this;
  };

  this.svg = function (x) {
    if (!arguments.length) return svg;
    svg = x;
    return this;
  };

  this.words = function (x) {
    if (!arguments.length) return words;
    words = x;
    return this;    
  }

  this.cloudObj = function () {
    return cloud;
  }

  this.start = function () {
    attempts++;
    cloud = d3.layout.cloud()
      .size(me.size())
      .words(words)
      .rotate(0)
      .fontSize(function(d) { return d.size; })
      .spiral("rectangular")
      .on("end", draw);

    svgToPixelArray(me.svg(), cloudW, cloudH, function (pixels32) {
      // if (attempts == 1)
        // drawPixelArray(pixels32, cloudW, cloudH);
      cloud.mask(pixels32)
        .randomPosition(function () {
              var w32 = cloudW >> 5;
              var block = valid_blocks[Math.floor(Math.random() * (valid_blocks.length - 1))];
              var coords = [(block % w32) << 5, Math.floor(block/w32)];
              return coords;
            })
        .start();
    });
  }

  function draw(theseWords) {
    var ratio = (1.0 * theseWords.length / words.length);
    if (ratio > maxForParams) {
      maxForParams = ratio;
      bestArrangementSoFar = theseWords;
    }
    if (ratio > 0.6 || attempts > 1) {
      attachToParent(bestArrangementSoFar || theseWords);
    }
    else me.start();
  }
  function attachToParent (words) {
    if (parent.empty()) {
      parent = d3.select("body").append("svg")
        .attr("width", cloudW)
        .attr("height", cloudH);
    }

    parent.append("g")
        .attr("class", "cloud")
        .attr("clip-path", "url(" + me.clip() + ")")
      .append("g")
        .attr("transform", "translate(" + cloudW/2 + "," + cloudH / 2 + ")")
      .selectAll("text")
        .data(words)
      .enter().append("text")
        .style("font-size", function(d) { return d.size + "px"; })
        .style("fill", d3.rgb(me.color()).darker(2))
        .attr("text-anchor", "middle")
        .attr("transform", function(d) {
          return "translate(" + [d.x, d.y] + ")rotate(" + d.rotate + ")";
        })
        .text(function(d) { return d.text; });
  }

  function pix32ize(pixels, width, height) {
    var ch = height,
        cw = width >> 5;
    var pixels32 = [];
    for (var i = 0; i < ch * cw; i++) pixels32[i] = 0;

    for (var j = 0; j < height; j++) {
      for (var i = 0; i < width; i++) {
          var k = cw * j + (i >> 5),
              m = pixels[(j * width + i) << 2] ? 1 << (31 - (i % 32)) : 0;
          pixels32[k] |= m;
      }
    }
    for (var i = 0; i < ch * cw; i++) {
      if (pixels32[i] | 0) {
        valid_blocks.push(i);
      }
      pixels32[i] = ~pixels32[i];
    }
   return pixels32;
  }

  function svgToPixelArray (svgText, width, height, callback) {
    var cw = width >> 5,
        ch = height,
        svgCanvas = document.createElement("canvas");

    svgCanvas.width = 1;
    svgCanvas.height = 1;
    var ratio = Math.sqrt(svgCanvas.getContext("2d").getImageData(0, 0, 1, 1).data.length >> 2);
    svgCanvas.width = width / ratio;
    svgCanvas.height = height / ratio;

    var c = svgCanvas.getContext("2d");

    var svgData = "<svg xmlns='http://www.w3.org/2000/svg' width='" + width + "' height='" + height + "'>"  +
      "<style type='text/css'>path { fill: #fff; stroke-width: 8; stroke: #000;}</style>" +
        svgText +
      "</svg>";

    c.drawSvg(svgData, 0, 0, width / ratio, height / ratio);
    var pixels = c.getImageData(0, 0, width / ratio, height / ratio).data;
    if (callback) callback(pix32ize(pixels, width, height));
  }

}