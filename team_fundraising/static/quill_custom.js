/**
 * Quill editor custom configuration and setup
 */

function initQuillEditor(editorId, messageTextareaId) {
  var quill = new Quill(editorId, {
    theme: 'snow',
    modules: {
      toolbar: [
        ['bold', 'italic', 'underline', 'strike'],
        ['blockquote'],
        [{ 'list': 'ordered'}, { 'list': 'bullet' }],
        [{ 'header': [1, 2, 3, 4, 5, 6, false] }],
        [{ 'color': [] }, { 'background': [] }],
        ['clean']
      ]
    }
  });
  
  // Make sure paragraphs have proper formatting by adding .spacer class
  quill.on('text-change', function() {
    var content = quill.root.innerHTML;
    document.querySelector(messageTextareaId).value = content;
  });
  
  return quill;
}
