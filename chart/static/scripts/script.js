function toggleInputCargo(){
    const cargoSelect = document.getElementById('cargo');
    const newCargoContainer = document.getElementById('new_cargo');
    
    if (cargoSelect.value === 'new') {
      newCargoContainer.style.display = 'block';
    } else {
      newCargoContainer.style.display = 'none';
    }
  }
  
// Executar a função no carregamento da página para configurar o estado inicial
document.addEventListener('DOMContentLoaded', toggleInputCargo);

function popupMessage(message){
    alert(message);
}