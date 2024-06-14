$(document).ready(function() {
    var entryIndex = 1;

    $('#add-entry').click(function() {
        var newEntry = $('.result-entry:first').clone();
        newEntry.find('input').val('');
        newEntry.find('.form-label').each(function() {
            var newFor = $(this).attr('for').replace('0', entryIndex);
            $(this).attr('for', newFor);
        });
        newEntry.find('.form-control').each(function() {
            var newId = $(this).attr('id').replace('0', entryIndex);
            var newName = $(this).attr('name').replace('0', entryIndex);
            $(this).attr('id', newId);
            $(this).attr('name', newName);
        });
        $('#results-list').append(newEntry);
        entryIndex++;
    });
});