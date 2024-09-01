function createTop10Charts() {
  var spreadsheet = SpreadsheetApp.getActiveSpreadsheet();
  var sheets = spreadsheet.getSheets();

  for (var s = 0; s < sheets.length; s++) {
    var sheet = sheets[s];
    var sheetName = sheet.getName();

    // Skip sheets named "Summary" and "5Days"
    if (sheetName === "Summary" || sheetName === "RecentDays") {
      continue;
    }

    // Check if charts already exist by title
    var existingCharts = sheet.getCharts();
    var chart1Exists = false;
    var chart2Exists = false;
    var chart3Exists = false;

    for (var i = 0; i < existingCharts.length; i++) {
      var chartTitle = existingCharts[i].getOptions().get('title');

      if (chartTitle === 'Top 10 ERROR Incidents') {
        chart1Exists = true;
      } else if (chartTitle === 'Top 10 WARN Incidents') {
        chart2Exists = true;
      } else if (chartTitle === 'Top 10 Custom Error Incidents') {
        chart3Exists = true;
      }
    }

    // Update or insert charts
    if (chart1Exists) {
      var chart1 = existingCharts.find(chart => chart.getOptions().get('title') === 'Top 10 WARN Incidents');
      chart1 = chart1.modify().removeRange(chart1.getRanges()[0]).addRange(sheet.getRange("A25:A36")).build();
      sheet.updateChart(chart1);
    } else {
      var chart1 = sheet.newChart()
        .setChartType(Charts.ChartType.BAR)
        .addRange(sheet.getRange("A25:A36"))
        .setPosition(5, 2, 0, 0)
        .setOption('title', 'Top 10 ERROR Incidents')
        .setOption('legend', { position: 'none' })
        .setOption('height', 300)
        .setOption('width', 600)
        .setOption('chartArea', { width: '50%' })
        .setOption('colors', ['red'])
        .setOption('vAxes', {
          0: {
            title: 'Incident',
            textStyle: { color: 'black' }
          }
        })
        .setOption('hAxis', {
          slantedText: true,
          slantedTextAngle: 45
        })
        .setOption('series', {
          0: {
            dataLabel: 'value'
          }
        })
        .build();
      sheet.insertChart(chart1);
    }

    if (chart2Exists) {
      var chart2 = existingCharts.find(chart => chart.getOptions().get('title') === 'Top 10 WARN Incidents');
      chart2 = chart2.modify().removeRange(chart2.getRanges()[0]).addRange(sheet.getRange("I25:I36")).build();
      sheet.updateChart(chart2);
    } else {
      var chart2 = sheet.newChart()
        .setChartType(Charts.ChartType.BAR)
        .addRange(sheet.getRange("I25:I36"))
        .setPosition(5, 9, 0, 0)
        .setOption('title', 'Top 10 WARN Incidents')
        .setOption('legend', { position: 'none' })
        .setOption('height', 300)
        .setOption('width', 600)
        .setOption('chartArea', { width: '50%' })
        .setOption('colors', ['orange'])
        .setOption('vAxes', {
          0: {
            title: 'Incident',
            textStyle: { color: 'black' }
          }
        })
        .setOption('hAxis', {
          slantedText: true,
          slantedTextAngle: 45
        })
        .setOption('series', {
          0: {
            dataLabel: 'value'
          }
        })
        .build();
      sheet.insertChart(chart2);
    }

    if (chart3Exists) {
      var chart3 = existingCharts.find(chart => chart.getOptions().get('title') === 'Top 10 Custom Error Incidents');
      chart3 = chart3.modify().removeRange(chart3.getRanges()[0]).addRange(sheet.getRange("P25:P36")).build();
      sheet.updateChart(chart3);
    } else {
      var chart3 = sheet.newChart()
        .setChartType(Charts.ChartType.BAR)
        .addRange(sheet.getRange("P25:P36"))
        .setPosition(5, 16, 0, 0)
        .setOption('title', 'Top 10 Custom Error Incidents')
        .setOption('legend', { position: 'none' })
        .setOption('height', 300)
        .setOption('width', 600)
        .setOption('chartArea', { width: '50%' })
        .setOption('colors', ['green'])
        .setOption('vAxes', {
          0: {
            title: 'Incident',
            textStyle: { color: 'black' }
          }
        })
        .setOption('hAxis', {
          slantedText: true,
          slantedTextAngle: 45
        })
        .setOption('series', {
          0: {
            dataLabel: 'value'
          }
        })
        .build();
      sheet.insertChart(chart3);
    }
  }
}
