function openMenu() {
    if (document.getElementById('menuBar').textContent == 'lll') {
        document.getElementById('Menu').style.display = 'block';
        document.getElementById('contentMain').style.display = 'none';
        document.getElementById('contentFooter').style.display = 'none';
        document.getElementById('menuBar').textContent = 'X';
        document.getElementById('menuBar').style.transform = 'rotate(0deg)';
    }

    else {
        document.getElementById('Menu').style.display = 'none';
        document.getElementById('contentMain').style.display = 'block';
        document.getElementById('contentFooter').style.display = 'block';
        document.getElementById('menuBar').textContent = 'lll';
        document.getElementById('menuBar').style.transform = 'rotate(90deg)';
    }

}