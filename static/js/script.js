/* global $, CodeMirror, d3 */
'use strict'

// http://bl.ocks.org/mbostock/4062045
// http://bl.ocks.org/mbostock/2706022
// http://bl.ocks.org/d3noob/5141278
$(document).ready(function () {
  // Navigation
  function onHashChange () {
    var location = window.location.hash.toLowerCase()
    if (['#home', '#help'].indexOf(location) === -1) {
      location = '#home'
    }
    $('.nav-main').hide()
    $(location).fadeIn()
    $('.nav > .active').removeClass('active')
    $("a[href='" + location + "']").parent().addClass('active')
  }
  onHashChange()
  $(window).on('hashchange', onHashChange)

  var globalData = null
  var lazyGraphData = {}
  var lazyProperties = {}
  var codeMirror = CodeMirror.fromTextArea($('#source_code')[0], {
    indentUnit: 2,
    lineNumbers: true,
    tabindex: -1,
    autofocus: true,
    showCursorWhenSelecting: true,
    viewportMargin: Infinity
  })

  $('#form').submit(function (e) {
    e.preventDefault()

    clearOutput()
    $.ajax({
      url: 'api',
      data: {
        source_code: $('#source_code').val()
      },
      dataType: 'json',
      method: 'POST',
      success: function (data) {
        if (data.hasOwnProperty('errors')) {
          $('#parse-errors').text(data.errors)
          return false
        }

        $('#statistics').html('')
        var stats = [
          '# Symbols: ' + data.statistics.symbols,
          '# Potential arguments: ' + data.statistics.potential_arguments,
          '# Arguments: ' + data.statistics.arguments,
          '# Assumptions: ' + data.statistics.assumptions,
          '# Conflict-free arguments: ' + data.statistics.is_conflict_free,
          '# Admissible arguments: ' + data.statistics.is_admissible,
          '# Complete arguments: ' + data.statistics.is_complete,
          '# Grounded arguments: ' + data.statistics.is_grounded,
          '# Ideal arguments: ' + data.statistics.is_ideal,
          '# Stable arguments: ' + data.statistics.is_stable,
          'Wall time: ' + data.statistics.wall_time + 's',
          'CPU time: ' + data.statistics.cpu_time + 's'
        ]
        $('#statistics').html(stats.join('<br/>'))

        $('#tab-output').addClass('in')
        $('#tab-output').height('auto')

        $('#debug').text(JSON.stringify(data))
        globalData = data

        drawD3ArgumentAdapter(data.arguments, 'argument')

        var keys = Object.keys(data.dispute_trees)
        keys.sort()

        for (var i = 0; i < keys.length; i++) {
          if (data.dispute_trees.hasOwnProperty(keys[i])) {
            addTabDisputeTree(keys[i], data.dispute_trees)
          }
        }
        $('#parse-errors').html('')
        if (data.parse_errors.length > 0) {
          $('#parse-errors').html(data.parse_errors.join('<br/>'))
        }
        $('a[data-toggle="tab"]').off('shown.bs.tab', handleTabShown)
        $('a[data-toggle="tab"]').on('shown.bs.tab', handleTabShown)

        var elementName = 'argument'
        var graph = lazyGraphData['argument']
        drawD3(graph, elementName)
      },
      error: function (jqXHR, textStatus, errorThrown) {
        console.error(jqXHR)
        console.error(textStatus)
        console.error(errorThrown)
        $('#debug').text(textStatus)
      }
    })
  })
  function handleTabShown (e) {
    if (e.target.hash === '#statistics') {
      return
    }
    var elementName = e.target.hash.replace('#output-', '')
    var graph = lazyGraphData[elementName]
    var curvy = lazyProperties[elementName].curvy

    drawD3(graph, elementName, curvy)
    if (lazyProperties[elementName].hasOwnProperty('properties')) {
      $('#output-dt-text-' + elementName).text(
        lazyProperties[elementName].properties
      )
    }

    if (e.relatedTarget) {
      var oldElementName = e.relatedTarget.hash
      if (oldElementName === '#statistics') {
        return
      }
      $(oldElementName).html('')
    }
  }
  function clearOutput () {
    $('#tab-output').removeClass('in')
    $('#tab-output').height($('#tab-output').height())
    $('.li-dt').remove()
    $('.output-dt').remove()
    $('svg').remove()
    $('#tab-output-list a:first').tab('show')
  }

  function addTabDisputeTree (name) {
    var tabListNew = $('<li/>', {
      class: 'li-dt',
      html: $('<a/>', {
        href: '#output-dt-' + name,
        'data-toggle': 'tab',
        text: 'Dispute Tree for ' + name
      })
    })

    $('#output-dropdown-dt').append(tabListNew)
    $(tabListNew).find('a').tab()
    $('#output-dropdown-toggle').dropdown()

    $('#tab-output-content')
      .append(
        $('<div/>', {
          class: 'tab-pane fade output-dt',
          id: 'output-dt-' + name,
          html: $('<div/>', {
            id: 'output-dt-text-dt-' + name
          })
        })
      )
      .promise()
      .done(function () {
        drawD3DisputeTreeAdapter(globalData.dispute_trees[name], name)
      })
  }
  function drawD3ArgumentAdapter (graph, elementName) {
    var i
    for (i = 0; i < graph.nodes.length; i++) {
      graph.nodes[i].text_label = graph.nodes[i].id.substring(
        0,
        graph.nodes[i].id.lastIndexOf(graph.nodes[i].group) - 1
      )
      graph.nodes[i].id =
        graph.nodes[i].text_label + '\nSupporting ' + graph.nodes[i].group
    }
    for (i = 0; i < graph.nodes.length; i++) {
      if (
        graph.nodes[i].id.lastIndexOf(graph.nodes[i].group) ===
          graph.nodes[i].id.length - graph.nodes[i].group.length &&
        graph.nodes[i].id.indexOf(graph.nodes[i].group) === 0
      ) {
        graph.nodes[i].group = 'root'
      }
    }
    for (i = 0; i < graph.nodes.length; i++) {
      if (graph.nodes[i].group === 'root') {
        graph.nodes[i].id = graph.nodes[i].text_label + '\n(Root)'
      }
    }
    lazyGraphData[elementName] = graph
    lazyProperties[elementName] = {
      curvy: false
    }
  }
  function drawD3DisputeTreeAdapter (rawGraph, name) {
    var graph = JSON.parse(rawGraph)
    for (var i = 0; i < graph.nodes.length; i++) {
      var newLabel = '(' + graph.nodes[i].label + ') ' + graph.nodes[i].id

      if (graph.nodes[i].id === name.substr(0, name.indexOf('_'))) {
        graph.nodes[i].group = 'root'
      }

      graph.nodes[i].id = graph.nodes[i].text_label
      graph.nodes[i].text_label = newLabel
    }

    lazyGraphData['dt-' + name] = graph
    lazyProperties['dt-' + name] = {
      curvy: true
    }

    showDisputeTreeText(name)
  }
  function showDisputeTreeText (name) {
    var properties = [
      'is_conflict_free',
      'is_stable',
      'is_admissible',
      'is_grounded',
      'is_ideal',
      'is_complete'
    ]
    var propertyText = [
      'conflict free',
      'stable',
      'admissible',
      'grounded',
      'ideal',
      'complete'
    ]
    var shownText = []
    for (var i = 0; i < properties.length; i++) {
      if (globalData.dispute_trees_data[name][properties[i]]) {
        shownText.push(propertyText[i])
      }
    }
    shownText = shownText.join(', ')
    shownText = shownText.charAt(0).toUpperCase() + shownText.slice(1)

    lazyProperties['dt-' + name] = {
      curvy: true,
      properties: shownText
    }
  }

  function rootColor () {
    return '#FF4136'
  }
  function drawD3 (graph, elementName) {
    var width = 750
    var height = 600
    var radius = 6
    var curvy = false
    if (arguments.length === 3) {
      curvy = arguments[2]
    }

    var color = d3.scale.category20()

    var force = d3.layout
      .force()
      .gravity(0.1)
      .charge(-350)
      .linkDistance(80)
      .size([width, height])

    var tip = d3
      .tip()
      .offset([-10, 0])
      .attr('class', 'd3-tip')
      .html(function (d) {
        return d.id.replace('\n', '<br />')
      })
    var tipEdge = d3
      .tip()
      .offset(function () {
        return [this.getBBox().height / 2 - 10, 0]
      })
      .attr('class', 'd3-tip')
      .html(function (d) {
        return d
      })

    d3.select('#output-' + elementName).select('svg').remove()

    var svg = d3
      .select('#output-' + elementName)
      .append('svg')
      .attr('width', width)
      .attr('height', height)
      .call(tip)
      .call(tipEdge)

    force.nodes(graph.nodes).links(graph.links).start()

    // build the arrow.
    // Note: http://jsfiddle.net/5qaL886d/1/ ; this breaks IE10

    var link = null
    if (elementName === 'argument') {
      svg
        .append('svg:defs')
        .selectAll('marker')
        .data(['end-' + elementName])
        .enter()
        .append('svg:marker')
        .attr('id', String)
        .attr('viewBox', '-7 -7 14 14')
        .attr('refX', 14)
        .attr('refY', 0)
        .attr('markerWidth', 6)
        .attr('markerHeight', 6)
        .attr('orient', 'auto')
        .append('svg:circle')
        .attr('r', 5)
        .style('fill', '#000')
      link = svg
        .append('svg:g')
        .selectAll('path')
        .data(graph.links)
        .enter()
        .append('svg:path')
        .attr('class', 'link')
        .attr('marker-end', 'url(#end-' + elementName + ')')
    } else {
      // Dispute tree

      svg
        .append('svg:defs')
        .selectAll('marker')
        .data(['start-' + elementName])
        .enter()
        .append('svg:marker')
        .attr('id', String)
        .attr('viewBox', '-10 -5 10 10')
        .attr('refX', -15)
        .attr('refY', 0)
        .attr('markerWidth', 6)
        .attr('markerHeight', 6)
        .attr('orient', 'auto')
        .append('svg:path')
        .attr('d', 'M0,5L-10,0L0,-5')
      link = svg
        .append('svg:g')
        .selectAll('path')
        .data(graph.links)
        .enter()
        .append('svg:path')
        .attr('class', 'link')
        .attr('marker-start', 'url(#start-' + elementName + ')')
    }

    var node = svg
      .selectAll('.node')
      .data(graph.nodes)
      .enter()
      .append('g')
      .attr('class', 'node')
      .call(force.drag)

    node
      .append('circle')
      .attr('class', 'node_circle')
      .attr('r', function (d) {
        return d.group === 'root' ? 6 : 5
      })
      .style('fill', function (d) {
        return d.group === 'root' ? rootColor(d.group) : color(d.group)
      })
      .on('mouseover', tip.show)
      .on('mouseout', tip.hide)

    node.append('text').attr('x', 12).attr('dy', '.35em').text(function (d) {
      return 'text_label' in d ? d.text_label : d.id
    })

    force.on('tick', function (e) {
      var k = 6 * e.alpha
      graph.links.forEach(function (d, i) {
        if ('depth' in d.source && 'depth' in d.target) {
          if (d.source.depth < d.target.depth) {
            d.source.y -= k
            d.target.y += k
          } else {
            d.source.y += k
            d.target.y -= k
          }
        } else {
          d.source.y -= k
          d.target.y += k
        }
        d.source.x = Math.max(radius, Math.min(width - radius, d.source.x))
        d.target.x = Math.max(radius, Math.min(width - radius, d.target.x))
        d.source.y = Math.max(radius, Math.min(width - radius, d.source.y))
        d.target.y = Math.max(radius, Math.min(width - radius, d.target.y))
      })

      node.attr('transform', function (d) {
        return (
          'translate(' +
          Math.max(radius, Math.min(width - radius, d.x)) +
          ',' +
          Math.max(radius, Math.min(height - radius, d.y)) +
          ')'
        )
      })

      link.attr('d', function (d) {
        var dx = d.target.x - d.source.x
        var dy = d.target.y - d.source.y
        var dr = Math.sqrt(dx * dx + dy * dy)
        if (!curvy) {
          dr = 0
        }
        return (
          'M' +
          d.source.x +
          ',' +
          d.source.y +
          'A' +
          dr +
          ',' +
          dr +
          ' 0 0,1 ' +
          d.target.x +
          ',' +
          d.target.y
        )
      })
    })
  }
})
