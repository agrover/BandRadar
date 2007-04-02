<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">

<?python
    from bandradar.widgets import artist_list
?>

<span xmlns:py="http://purl.org/kid/ns#" class="artistlist">${XML(artist_list.get_list(artists))}</span>
