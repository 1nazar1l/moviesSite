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

document.addEventListener('DOMContentLoaded', function() {
  const vpnCheckbox = document.getElementById('vpn_connected');
  const idsCheckbox = document.getElementById('get_media_items_id');
  const submitButton = document.querySelector('.continue_button');
  const startPageInput = document.getElementById('start_page');
  const endPageInput = document.getElementById('end_page');

  const vpnDependentElements = [
    {
      element: document.getElementById('get_media_items_id'),
      block: document.querySelector('#get_media_items_id').closest('.input_block.checkbox_type')
    },
    {
      element: document.getElementById('start_page'),
      block: document.querySelector('#start_page').closest('.input_block.text_type')
    },
    {
      element: document.getElementById('end_page'),
      block: document.querySelector('#end_page').closest('.input_block.text_type')
    },
    {
      element: document.getElementById('get_media_items_data'),
      block: document.querySelector('#get_media_items_data').closest('.input_block.checkbox_type')
    },
    {
      element: document.getElementById('download_images'),
      block: document.querySelector('#download_images').closest('.input_block.checkbox_type')
    }
  ];

  function toggleVpnDependentElements() {
    const isVpnConnected = vpnCheckbox.checked;
    
    vpnDependentElements.forEach(item => {
      if (item.element && item.block) {
        item.element.disabled = !isVpnConnected;
        item.block.classList.toggle('disabled', !isVpnConnected);
        
        if (!isVpnConnected && item.element.type === 'checkbox' && item.element.checked) {
          item.element.checked = false;
        }
      }
    });
  }

  toggleVpnDependentElements();

  function validatePageNumbers() {
    const isVpnConnected = vpnCheckbox.checked;
    const getMediaIds = idsCheckbox.checked;
    const startValue = startPageInput.value.trim();
    const endValue = endPageInput.value.trim();

    if (isVpnConnected && getMediaIds) {

      // Проверка на пустые значения
      if (!startValue || !endValue) {
        alert('Оба поля (начальная и конечная страница) должны быть заполнены!');
        return false;
      }
      
      // Проверка что значения - целые числа
      if (!/^\d+$/.test(startValue) || !/^\d+$/.test(endValue)) {
        alert('Введите целые положительные числа в оба поля!');
        return false;
      }
      
      const startNum = parseInt(startValue);
      const endNum = parseInt(endValue);
      
      // Проверка что числа больше 0
      if (startNum <= 0 || endNum <= 0) {
        alert('Числа должны быть больше нуля!');
        return false;
      }

      if (startNum > 500 || endNum > 500) {
        alert('Максимально допустимая страница 500!');
        return false;
      }
      
      // Проверка что начальная страница не больше конечной
      if (startNum > endNum) {
        alert('Начальная страница не может быть больше конечной!');
        return false;
      }
    }

    return true;
  }

  submitButton.addEventListener('click', function(e) {
    if (!validatePageNumbers()) {
      e.preventDefault();
      return false;
    }
    
    return confirm('Начать?');
  });

  vpnCheckbox.addEventListener('change', toggleVpnDependentElements);
});