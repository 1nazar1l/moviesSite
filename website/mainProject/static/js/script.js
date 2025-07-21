startPage = document.getElementById('start_page'); 
endPage = document.getElementById('end_page'); 

startPage.addEventListener('input', function() {
  if (startPage.value.trim() !== '') {
    startPage.classList.add('active')
  } else {
    startPage.classList.remove('active')
  }
});

endPage.addEventListener('input', function() {
  if (endPage.value.trim() !== '') {
    endPage.classList.add('active')
  } else {
    endPage.classList.remove('active')
  }
});