
function paginatePrazo() {
    document.addEventListener('DOMContentLoaded', function () {
      var tablePrazo = document.getElementById('body-noPrazo');
      var pageIndicatorPrazo = document.getElementById('page-indicator-prazo');
      var currentPagePrazo = 1;
      var rowsPerPagePrazo = 400;
  
      function updateTablePrazo() {
        
        var start = (currentPagePrazo - 1) * rowsPerPagePrazo;
        var end = start + rowsPerPagePrazo;
  
        for (var i = 0; i < tablePrazo.rows.length; i++) {
          tablePrazo.rows[i].style.display = 'none';
        }
  
        for (var i = start; i < end && i < tablePrazo.rows.length; i++) {
          tablePrazo.rows[i].style.display = '';
        }
  
        pageIndicatorPrazo.textContent = 'Página ' + currentPagePrazo;
      }
  
      function goToPagePrazo(page) {
        if (page >= 1 && page <= Math.ceil(tablePrazo.rows.length / rowsPerPagePrazo)) {
          currentPagePrazo = page;
          updateTablePrazo();
        }
      }
  
      function goToFirstPagePrazo() {
        goToPagePrazo(1);
      }
  
      function goToLastPagePrazo() {
        goToPagePrazo(Math.ceil(tablePrazo.rows.length / rowsPerPagePrazo));
      }
  
      function goToPreviousPagePrazo() {
        goToPagePrazo(currentPagePrazo - 1);
      }
  
      function goToNextPagePrazo() {
        goToPagePrazo(currentPagePrazo + 1);
      }
  
      document.getElementById('btn-first-prazo').addEventListener('click', goToFirstPagePrazo);
      document.getElementById('btn-last-prazo').addEventListener('click', goToLastPagePrazo);
      document.getElementById('btn-previous-prazo').addEventListener('click', goToPreviousPagePrazo);
      document.getElementById('btn-next-prazo').addEventListener('click', goToNextPagePrazo);
  
      updateTablePrazo();
    });
}

function paginatePrazoCompra() {
    document.addEventListener('DOMContentLoaded', function () {
      var tablePrazoCompra = document.getElementById('body-noPrazo-compra');
      var pageIndicatorPrazoCompra = document.getElementById('page-indicator-prazo-compra');
      var currentPagePrazoCompra = 1;
      var rowsPerPagePrazoCompra = 400;
  
      function updateTablePrazoCompra() {
        var start = (currentPagePrazoCompra - 1) * rowsPerPagePrazoCompra;
        var end = start + rowsPerPagePrazoCompra;
  
        for (var i = 0; i < tablePrazoCompra.rows.length; i++) {
          tablePrazoCompra.rows[i].style.display = 'none';
        }
  
        for (var i = start; i < end && i < tablePrazoCompra.rows.length; i++) {
          tablePrazoCompra.rows[i].style.display = '';
        }
  
        pageIndicatorPrazoCompra.textContent = 'Página ' + currentPagePrazoCompra;
      }
  
      function goToPagePrazoCompra(page) {
        if (page >= 1 && page <= Math.ceil(tablePrazoCompra.rows.length / rowsPerPagePrazoCompra)) {
          currentPagePrazoCompra = page;
          updateTablePrazoCompra();
        }
      }
  
      function goToFirstPagePrazoCompra() {
        goToPagePrazoCompra(1);
      }
  
      function goToLastPagePrazoCompra() {
        goToPagePrazoCompra(Math.ceil(tablePrazoCompra.rows.length / rowsPerPagePrazoCompra));
      }
  
      function goToPreviousPagePrazoCompra() {
        goToPagePrazoCompra(currentPagePrazoCompra - 1);
      }
  
      function goToNextPagePrazoCompra() {
        goToPagePrazoCompra(currentPagePrazoCompra + 1);
      }
  
      document.getElementById('btn-first-prazo-compra').addEventListener('click', goToFirstPagePrazoCompra);
      document.getElementById('btn-last-prazo-compra').addEventListener('click', goToLastPagePrazoCompra);
      document.getElementById('btn-previous-prazo-compra').addEventListener('click', goToPreviousPagePrazoCompra);
      document.getElementById('btn-next-prazo-compra').addEventListener('click', goToNextPagePrazoCompra);
  
      updateTablePrazoCompra();
    });
}

function paginateAtraso() {
    document.addEventListener('DOMContentLoaded', function () {
      var tableAtraso = document.getElementById('body-atrasados');
      var pageIndicatorAtraso = document.getElementById('page-indicator-atraso');
      var currentPageAtraso = 1;
      var rowsPerPageAtraso = 400;
  
      function updateTableAtraso() {
        var start = (currentPageAtraso - 1) * rowsPerPageAtraso;
        var end = start + rowsPerPageAtraso;
  
        for (var i = 0; i < tableAtraso.rows.length; i++) {
          tableAtraso.rows[i].style.display = 'none';
        }
  
        for (var i = start; i < end && i < tableAtraso.rows.length; i++) {
          tableAtraso.rows[i].style.display = '';
        }
  
        pageIndicatorAtraso.textContent = 'Página ' + currentPageAtraso;
      }
  
      function goToPageAtraso(page) {
        if (page >= 1 && page <= Math.ceil(tableAtraso.rows.length / rowsPerPageAtraso)) {
          currentPageAtraso = page;
          updateTableAtraso();
        }
      }
  
      function goToFirstPageAtraso() {
        goToPageAtraso(1);
      }
  
      function goToLastPageAtraso() {
        goToPageAtraso(Math.ceil(tableAtraso.rows.length / rowsPerPageAtraso));
      }
  
      function goToPreviousPageAtraso() {
        goToPageAtraso(currentPageAtraso - 1);
      }
  
      function goToNextPageAtraso() {
        goToPageAtraso(currentPageAtraso + 1);
      }
  
      document.getElementById('btn-first-atraso').addEventListener('click', goToFirstPageAtraso);
      document.getElementById('btn-last-atraso').addEventListener('click', goToLastPageAtraso);
      document.getElementById('btn-previous-atraso').addEventListener('click', goToPreviousPageAtraso);
      document.getElementById('btn-next-atraso').addEventListener('click', goToNextPageAtraso);
  
      updateTableAtraso();
    });
}

function paginateAtrasoCompra() {
        document.addEventListener('DOMContentLoaded', function () {
          var tableAtrasoCompra = document.getElementById('body-atrasados-compra');
          var pageIndicatorAtrasoCompra = document.getElementById('page-indicator-atraso-compra');
          var currentPageAtrasoCompra = 1;
          var rowsPerPageAtrasoCompra = 400;
      
          function updateTableAtrasoCompra() {
            var start = (currentPageAtrasoCompra - 1) * rowsPerPageAtrasoCompra;
            var end = start + rowsPerPageAtrasoCompra;
      
            for (var i = 0; i < tableAtrasoCompra.rows.length; i++) {
              tableAtrasoCompra.rows[i].style.display = 'none';
            }
      
            for (var i = start; i < end && i < tableAtrasoCompra.rows.length; i++) {
              tableAtrasoCompra.rows[i].style.display = '';
            }
      
            pageIndicatorAtrasoCompra.textContent = 'Página ' + currentPageAtrasoCompra;
          }
      
          function goToPageAtrasoCompra(page) {
            if (page >= 1 && page <= Math.ceil(tableAtrasoCompra.rows.length / rowsPerPageAtrasoCompra)) {
              currentPageAtrasoCompra = page;
              updateTableAtrasoCompra();
            }
          }
      
          function goToFirstPageAtrasoCompra() {
            goToPageAtrasoCompra(1);
          }
      
          function goToLastPageAtrasoCompra() {
            goToPageAtrasoCompra(Math.ceil(tableAtrasoCompra.rows.length / rowsPerPageAtrasoCompra));
          }
      
          function goToPreviousPageAtrasoCompra() {
            goToPageAtrasoCompra(currentPageAtrasoCompra - 1);
          }
      
          function goToNextPageAtrasoCompra() {
            goToPageAtrasoCompra(currentPageAtrasoCompra + 1);
          }
      
          document.getElementById('btn-first-atraso-compra').addEventListener('click', goToFirstPageAtrasoCompra);
          document.getElementById('btn-last-atraso-compra').addEventListener('click', goToLastPageAtrasoCompra);
          document.getElementById('btn-previous-atraso-compra').addEventListener('click', goToPreviousPageAtrasoCompra);
          document.getElementById('btn-next-atraso-compra').addEventListener('click', goToNextPageAtrasoCompra);
      
          updateTableAtrasoCompra();
        });
}

function paginateindeterminados() {
    document.addEventListener('DOMContentLoaded', function () {
      var tableindeterminados = document.getElementById('body-indeterminados');
      var pageIndicatorindeterminados = document.getElementById('page-indicator-indeterminados');
      var currentPageindeterminados = 1;
      var rowsPerPageindeterminados = 400;
  
      function updateTableindeterminados() {
        var start = (currentPageindeterminados - 1) * rowsPerPageindeterminados;
        var end = start + rowsPerPageindeterminados;
  
        for (var i = 0; i < tableindeterminados.rows.length; i++) {
          tableindeterminados.rows[i].style.display = 'none';
        }
  
        for (var i = start; i < end && i < tableindeterminados.rows.length; i++) {
          tableindeterminados.rows[i].style.display = '';
        }
  
        pageIndicatorindeterminados.textContent = 'Página ' + currentPageindeterminados;
      }
  
      function goToPageindeterminados(page) {
        if (page >= 1 && page <= Math.ceil(tableindeterminados.rows.length / rowsPerPageindeterminados)) {
          currentPageindeterminados = page;
          updateTableindeterminados();
        }
      }
  
      function goToFirstPageindeterminados() {
        goToPageindeterminados(1);
      }
  
      function goToLastPageindeterminados() {
        goToPageindeterminados(Math.ceil(tableindeterminados.rows.length / rowsPerPageindeterminados));
      }
  
      function goToPreviousPageindeterminados() {
        goToPageindeterminados(currentPageindeterminados - 1);
      }
  
      function goToNextPageindeterminados() {
        goToPageindeterminados(currentPageindeterminados + 1);
      }
  
      document.getElementById('btn-first-indeterminados').addEventListener('click', goToFirstPageindeterminados);
      document.getElementById('btn-last-indeterminados').addEventListener('click', goToLastPageindeterminados);
      document.getElementById('btn-previous-indeterminados').addEventListener('click', goToPreviousPageindeterminados);
      document.getElementById('btn-next-indeterminados').addEventListener('click', goToNextPageindeterminados);
  
      updateTableindeterminados();
    });
}

function paginateindeterminadosCompra() {
  document.addEventListener('DOMContentLoaded', function () {
    var tableindeterminadosCompra = document.getElementById('body-indeterminados-compra');
    var pageIndicatorindeterminadosCompra = document.getElementById('page-indicator-indeterminados-compra');
    var currentPageindeterminadosCompra = 1;
    var rowsPerPageindeterminadosCompra = 400;

    function updateTableindeterminadosCompra() {
      var start = (currentPageindeterminadosCompra - 1) * rowsPerPageindeterminadosCompra;
      var end = start + rowsPerPageindeterminadosCompra;

      for (var i = 0; i < tableindeterminadosCompra.rows.length; i++) {
        tableindeterminadosCompra.rows[i].style.display = 'none';
      }

      for (var i = start; i < end && i < tableindeterminadosCompra.rows.length; i++) {
        tableindeterminadosCompra.rows[i].style.display = '';
      }

      pageIndicatorindeterminadosCompra.textContent = 'Página ' + currentPageindeterminadosCompra;
    }

    function goToPageindeterminadosCompra(page) {
      if (page >= 1 && page <= Math.ceil(tableindeterminadosCompra.rows.length / rowsPerPageindeterminadosCompra)) {
        currentPageindeterminadosCompra = page;
        updateTableindeterminadosCompra();
      }
    }

    function goToFirstPageindeterminadosCompra() {
      goToPageindeterminadosCompra(1);
    }

    function goToLastPageindeterminadosCompra() {
      goToPageindeterminadosCompra(Math.ceil(tableindeterminadosCompra.rows.length / rowsPerPageindeterminadosCompra));
    }

    function goToPreviousPageindeterminadosCompra() {
      goToPageindeterminadosCompra(currentPageindeterminadosCompra - 1);
    }

    function goToNextPageindeterminadosCompra() {
      goToPageindeterminadosCompra(currentPageindeterminadosCompra + 1);
    }

    document.getElementById('btn-first-indeterminados-compra').addEventListener('click', goToFirstPageindeterminadosCompra);
    document.getElementById('btn-last-indeterminados-compra').addEventListener('click', goToLastPageindeterminadosCompra);
    document.getElementById('btn-previous-indeterminados-compra').addEventListener('click', goToPreviousPageindeterminadosCompra);
    document.getElementById('btn-next-indeterminados-compra').addEventListener('click', goToNextPageindeterminadosCompra);

    updateTableindeterminadosCompra();
  });
}

paginatePrazo()
paginatePrazoCompra()
paginateAtraso()
paginateAtrasoCompra()
paginateindeterminados()
paginateindeterminadosCompra()