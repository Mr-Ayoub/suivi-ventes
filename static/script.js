// Montre un aperçu de l'image sélectionnée
document.addEventListener('DOMContentLoaded', function() {
    const inputPhoto = document.querySelector('input[name="photo"]');
    const form = document.getElementById('form');

    if (inputPhoto) {
        inputPhoto.addEventListener('change', function(event) {
            const file = event.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    let imgPreview = document.getElementById('imgPreview');
                    if (!imgPreview) {
                        imgPreview = document.createElement('img');
                        imgPreview.id = 'imgPreview';
                        imgPreview.style.maxWidth = '200px';
                        imgPreview.style.marginTop = '10px';
                        form.appendChild(imgPreview);
                    }
                    imgPreview.src = e.target.result;
                };
                reader.readAsDataURL(file);
            }
        });
    }
});
