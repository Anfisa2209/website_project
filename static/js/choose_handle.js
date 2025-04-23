document.addEventListener('DOMContentLoaded', function() {
    const colorRadios = document.querySelectorAll('input[name="handle_color"]');
    const modelRadios = document.querySelectorAll('input[name="handle_models"]');
    const previewImage = document.getElementById('handle-preview-image');

    function updateHandlePreview() {
        const selectedColor = document.querySelector('input[name="handle_color"]:checked')?.value;
        const selectedModel = document.querySelector('input[name="handle_models"]:checked')?.value;

        if(selectedColor && selectedModel) {
            const colorMap = {
                '1': 'серебро',
                '2': 'бронза',
                '3': 'белая',
                '4': 'коричневая'
            };

            const modelMap = {
                '1': 'односторонняя',
                '2': 'двухсторонняя'
            };

            const imagePath = `/static/img/calculate_form_img/handles/${colorMap[selectedColor]} ${modelMap[selectedModel]}.jpg`;
            previewImage.src = imagePath;
            previewImage.style.display = 'block';
        }
    }

    colorRadios.forEach(radio => radio.addEventListener('change', updateHandlePreview));
    modelRadios.forEach(radio => radio.addEventListener('change', updateHandlePreview));
});