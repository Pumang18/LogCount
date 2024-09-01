function createBarChart(sheet) {
  var charts = sheet.getCharts();
  for (var i = 0; i < charts.length; i++) {
    sheet.removeChart(charts[i]);
  }
  // Define the starting row and column
  var startRow = 21;
  var lastRow = sheet.getLastRow();

  // Chart configurations
  var chartsConfig = [
    {
      range: sheet.getRange(startRow, 2, lastRow - startRow + 1),
      position: {row: 2, column: 1},
      title: 'Recent Days Errors',
      color: 'red'
    },
    {
      range: sheet.getRange(startRow, 4, lastRow - startRow + 1),
      position: {row: 2, column: 7},
      title: 'Recent Days Warn',
      color: 'orange'
    },
    {
      range: sheet.getRange(startRow, 6, lastRow - startRow + 1),
      position: {row: 2, column: 13},
      title: 'Recent Days Custom Error',
      color: 'green'
    }
  ];

  // Retrieve existing charts
  var existingCharts = sheet.getCharts();

  chartsConfig.forEach(function(chartConfig) {
    var chartToUpdate = null;

    // Find existing chart by checking its ID or some other identifier
    for (var i = 0; i < existingCharts.length; i++) {
      var existingChart = existingCharts[i];
      var chartId = existingChart.getId(); // Get the chart ID

      // Determine if this is the chart we want to update based on position or other criteria
      var pos = existingChart.getContainerInfo().getAnchorColumn(); // Example of getting anchor column

      if (pos === chartConfig.position.column) {
        chartToUpdate = existingChart;
        break;
      }
    }

    if (chartToUpdate) {
      // Update existing chart
      var modifiedChart = chartToUpdate.modify()
        .addRange(chartConfig.range)
        .setOption('title', chartConfig.title)
        .setOption('hAxis', {title: 'Categories'})
        .setOption('vAxis', {title: 'Values'})
        .setOption('colors', [chartConfig.color])
        .build();

      sheet.updateChart(modifiedChart);
    } else {
      // Create new chart
      var newChart = sheet.newChart()
        .setChartType(Charts.ChartType.COLUMN)
        .addRange(chartConfig.range)
        .setPosition(chartConfig.position.row, chartConfig.position.column, 0, 0)
        .setOption('title', chartConfig.title)
        .setOption('hAxis', {title: 'Categories'})
        .setOption('vAxis', {title: 'Values'})
        .setOption('colors', [chartConfig.color])
        .build();

      sheet.insertChart(newChart);
    }
  });
}

function getRecentDays() {
  var sheets = SpreadsheetApp.getActiveSpreadsheet().getSheets();

  for (var i = 0; i < sheets.length; i++) {
    var sheet = sheets[i];
    if (sheet.getName() === "RecentDays") {
      createBarChart(sheet);
    }
  }
}