function createCharts(sheet) {
  var lastRow = sheet.getLastRow();
  var dataRange = sheet.getRange(2, 1, lastRow - 1, 4); // Assuming columns A to D

  // Clear existing charts (if any)
  var charts = sheet.getCharts();
  for (var i = 0; i < charts.length; i++) {
    sheet.removeChart(charts[i]);
  }

  // Chart for Day vs Total ERROR
  var chart1 = sheet.newChart()
    .setChartType(Charts.ChartType.LINE)
    .addRange(dataRange.offset(0, 0, lastRow - 1, 1))
    .addRange(dataRange.offset(0, 1, lastRow - 1, 1))
    .setPosition(3, 6, 0, 0)
    .setOption('title', 'Total ERROR Incidents')
    .setOption('width',1200)
    .setOption('height',600)
    .build();

  // Modify for point with size and data label, and set line color to red
  chart1 = modifyChart(chart1, 0, 'red', 'Total ERROR Incidents');
  sheet.insertChart(chart1);

  // Chart for Day vs Total WARN
  var chart2 = sheet.newChart()
    .setChartType(Charts.ChartType.LINE)
    .addRange(dataRange.offset(0, 0, lastRow - 1, 1))
    .addRange(dataRange.offset(0, 2, lastRow - 1, 1))
    .setOption('title', 'Total WARN Incidents')
    .setPosition(33, 6, 0, 0)
    .setOption('width',1200)
    .setOption('height',600)
    .build();

  // Modify for point with size and data label, and set line color to red
  chart2 = modifyChart(chart2, 0, 'orange', 'Total WARN Incidents');
  sheet.insertChart(chart2);

  // Chart for Day vs Total Custom Error
  var chart3 = sheet.newChart()
    .setChartType(Charts.ChartType.LINE)
    .addRange(dataRange.offset(0, 0, lastRow - 1, 1))
    .addRange(dataRange.offset(0, 3, lastRow - 1, 1))
    .setOption('title', 'Total CUSTOM WARN Incidents')
    .setPosition(63, 6, 0, 0)
    .setOption('width',1200)
    .setOption('height',600)
    .build();

  // Modify for point with size and data label, and set line color to red
  chart3 = modifyChart(chart3, 0, 'green', 'Total CUSTOM ERROR Incidents');
  sheet.insertChart(chart3);
}

// Function to modify chart for point with size, data label, and line color
function modifyChart(chart, seriesIndex, lineColor, seriesName) {
  var options = {
    pointSize: 8, // Adjust size of points as needed
    series: {},
    colors: [lineColor] // Set line color
  };

  options.series[seriesIndex] = { pointSize: 6, dataLabel: 'value' };

  // Apply options
  var modifiedChart = chart.modify()
    .setOption('series', options.series)
    .setOption('colors', options.colors)
    .setOption('title', seriesName)
    .build();

  return modifiedChart;
}

// Function to iterate through all spreadsheets and their sheets
function getSummary() {
  var sheets = SpreadsheetApp.getActiveSpreadsheet().getSheets();

  for (var i = 0; i < sheets.length; i++) {
    var sheet = sheets[i];
    if (sheet.getName() === "Summary") {
      createCharts(sheet);
    }
  }
}
