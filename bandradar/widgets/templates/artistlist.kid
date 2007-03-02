<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">

<?python
    from bandradar.widgets import artistlist
?>

<span xmlns:py="http://purl.org/kid/ns#" class="artistlist">
    ${XML(artistlist.get_list(event))}
</span>
