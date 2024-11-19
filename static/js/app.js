const successCloseBtn = document.getElementById('success-close-btn')
if (successCloseBtn) {
	successCloseBtn.addEventListener('click', function () {
		console.log('Close button clicked')
		document.getElementById('success-toast').innerHTML = ''
		successCloseBtn.removeEventListener('click', function () {
			console.log('removed event listener')
		})
	})
}

const errorCloseBtn = document.getElementById('error-close-btn')
if (errorCloseBtn) {
	errorCloseBtn.addEventListener('click', function () {
		console.log('Close button clicked')
		document.getElementById('error-toast').innerHTML = ''
		errorCloseBtn.removeEventListener('click', function () {
			console.log('removed event listener')
		})
	})
}




