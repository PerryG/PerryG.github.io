// Heaving inspired by http://simonsarris.com/project/canvasdemo/shapes.js
// Some code shamelessly stolen

function Point(x, y) {
    this.x = x;
    this.y = y;
}

// Returns the distance between two points
function dist(p0, p1) {
    return Math.sqrt(Math.pow(p0.x - p1.x, 2) + Math.pow(p0.y - p1.y, 2));
}

// Returns p1 - p0
function sub(p1, p0) {
    return new Point(p1.x - p0.x, p1.y - p0.y);
}

// c is location of center, r is radius, fill is color, default black
function Circle(c, r, fill, label) {
    this.c = c;
    this.r = r;
    this.fill = fill || '#000000';
    this.label = label;
}

Circle.prototype.draw = function(ctx) {
    ctx.beginPath(); 
    ctx.fillStyle = this.fill;
    ctx.arc(this.c.x, this.c.y, this.r, 0, 2*Math.PI);
    ctx.fill();
    ctx.font="20px Arial";
    ctx.fillText(this.label, this.c.x, this.c.y+this.r+20)
    ctx.stroke();
}

Circle.prototype.contains = function(p) {
    return dist(this.c, p) <= this.r;
}

function Line(p0, p1, width, style) {
    this.p0 = p0;
    this.p1 = p1;
    this.width = width || '2';
    this.style = style || '#000000';
}

Line.prototype.draw = function(ctx) {
    ctx.beginPath();
    ctx.lineWidth = this.width;
    ctx.strokeStyle = this.style;
    ctx.moveTo(this.p0.x, this.p0.y);
    ctx.lineTo(this.p1.x, this.p1.y);
    ctx.stroke();
}

// p0 should be upper left, p1 upper right, h is height
// (negative height will make lower left and lower right)
function Rectangle(p0, p1, h, lineWidth) {
    if (p1.x < p0.x)
        this.p0 = p1;
    else
        this.p0 = p0;
    this.w = dist(p0, p1);
    this.h = h;
    this.lineWidth = lineWidth || "3";
    var vector = sub(p1, p0);
    this.angle = Math.atan(vector.y / vector.x);
}

Rectangle.prototype.draw = function(ctx) {
    ctx.save();
    ctx.translate(this.p0.x, this.p0.y)
    ctx.lineWidth = this.lineWidth;
    ctx.rotate(this.angle);
    ctx.strokeRect(0, 0, this.w, this.h);
    var area = ((this.w * this.h) / 100).toFixed(0);
    ctx.translate(this.w / 2, this.h / 2);
    ctx.rotate(-this.angle);
    ctx.font="30px Arial";
    ctx.fillStyle = '#000000';
    ctx.fillText(area, 0, 0);
    ctx.restore();
}

function Square(p0, p1, lineWidth) {
    return new Rectangle(p0, p1, dist(p0, p1), lineWidth);
}

// This is a part really stolen from Simon Harris
function CanvasState(canvas) {
    this.canvas = canvas;
    this.width = canvas.width;
    this.height = canvas.height;
    this.ctx = canvas.getContext('2d');
    // This is a part really REALLY stolen (meaning, stolen without understanding)
    var stylePaddingLeft, stylePaddingTop, styleBorderLeft, styleBorderTop;
    if (document.defaultView && document.defaultView.getComputedStyle) {
        this.stylePaddingLeft = parseInt(document.defaultView.getComputedStyle(canvas, null)['paddingLeft'], 10)      || 0;
        this.stylePaddingTop  = parseInt(document.defaultView.getComputedStyle(canvas, null)['paddingTop'], 10)       || 0;
        this.styleBorderLeft  = parseInt(document.defaultView.getComputedStyle(canvas, null)['borderLeftWidth'], 10)  || 0;
        this.styleBorderTop   = parseInt(document.defaultView.getComputedStyle(canvas, null)['borderTopWidth'], 10)   || 0;
    }
    var html = document.body.parentNode;
    this.htmlTop = html.offsetTop;
    this.htmlLeft = html.offsetLeft;

    // OK, bullshit is out of the way. Back to normal stolen (stolen with understanding)
    this.reset();

    // Why the fuck is 'this' so dumb in javascript...
    var state = this;

    canvas.addEventListener('mousedown', function(e) {
        var mouse = state.getMouse(e);
        var circles = state.allCircles;

        for (var i = circles.length - 1; i >= 0; i--) {
            if (circles[i].contains(mouse)) {
                state.dragoffsetx = mouse.x - circles[i].c.x;
                state.dragoffsety = mouse.y - circles[i].c.y;
                state.refresh = true;
                state.selection = circles[i];
                return;
            }
        }
    }, true);

    canvas.addEventListener('mousemove', function(e) {
        if (state.selection) {
            var mouse = state.getMouse(e);
            state.selection.c.x = mouse.x - state.dragoffsetx;
            state.selection.c.y = mouse.y - state.dragoffsety;
            state.refresh = true;
        }
    }, true);

    canvas.addEventListener('mouseup', function(e) {
        state.selection = null;
    }, true);

    canvas.addEventListener('dblclick', function(e) {
        var mouse = state.getMouse(e);
        var newData = state.addData(mouse);
    }, true);

    this.interval = 30;
    setInterval(function() {state.draw();}, state.interval);
}

CanvasState.prototype.addCircle = function(p, type, label) {
    var label = label || '';
    var type = type || 'data';
    var style = null;
    switch (type) {
        case 'mean':
            style = '#FF0000';
            break;
        case 'median':
            style = '#00FF00';
            break;
        case 'data':
        default:
            style = null;
    }
    var newCircle = new Circle(p, 10, style, '');
    this.refresh = true;
    if (type == 'mean')
        this.means.push(newCircle);
    if (type == 'median')
        this.medians.push(newCircle)
    if (type == 'data') 
        this.data.push(newCircle);
    this.allCircles.push(newCircle);
    return newCircle;
}

CanvasState.prototype.addData = function(p) {
    return this.addCircle(p, 'data', '');
}

CanvasState.prototype.addMean = function() {
    var x = 0, y = 0;
    if (this.data.length == 0) {
        x = this.width / 2, y = this.height / 2;
    }
    else {
        for (var i = 0; i < this.data.length; i++) {
            x += this.data[i].c.x;
            y += this.data[i].c.y;
        }
        x = x / this.data.length;
        y = y / this.data.length;
    }
    return this.addCircle(new Point(x, y), 'mean', '');
}

CanvasState.prototype.clear = function() {
    this.ctx.clearRect(0, 0, this.width, this.height);
}

CanvasState.prototype.draw = function() {
    if (this.refresh) {
        this.clear();
        for (var i = 0; i < this.data.length; i++) {
            this.data[i].draw(this.ctx);
        }

        for (var i = 0; i < this.means.length; i++) {
            var sum = 0;
            for (var j = 0; j < this.data.length; j++) {
                (new Square(this.means[i].c, this.data[j].c, 1)).draw(this.ctx);
                sum += Math.pow(dist(this.means[i].c, this.data[j].c), 2);
            }
            this.means[i].label = (sum / 100).toFixed(0).toString();
            this.means[i].draw(this.ctx);
        }

        this.refresh = false;
    }
}

CanvasState.prototype.reset = function() {
    this.refresh = true;
    this.selection = null;
    this.data = [];
    this.means = [];
    this.medians = [];
    this.allCircles = [];
    this.dragoffsetx = 0;
    this.dragoffsety = 0;
}

// Take what you can, give nothing back!
CanvasState.prototype.getMouse = function(e) {
  var element = this.canvas, offsetX = 0, offsetY = 0;
  
  if (element.offsetParent !== undefined) {
    do {
      offsetX += element.offsetLeft;
      offsetY += element.offsetTop;
    } while ((element = element.offsetParent));
  }

  offsetX += this.stylePaddingLeft + this.styleBorderLeft + this.htmlLeft;
  offsetY += this.stylePaddingTop + this.styleBorderTop + this.htmlTop;

  return new Point(e.pageX - offsetX, e.pageY - offsetY);
}

function init() {
    var s = new CanvasState(document.getElementById('myCanvas'));
    $('#addMean').click(function() { s.addMean(); });
    $('#reset').click(function() { s.reset(); });
}



init();
