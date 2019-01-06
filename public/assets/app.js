(function()
{
    var form = document.forms[0], xhr
      , images_cont = document.getElementById('images')

    form.addEventListener('submit', function(e)
    {
        e.preventDefault()

        var fd = new FormData, template

        fd.append( 'names', this.querySelector('[name="names"]').value.trim() )

        if ( ! fd.get('names') )
            return this.querySelector('[name="names"]').focus()

        fd.append( 'fontsize', parseInt( this.querySelector('[name="fontsize"]').value ) )

        if ( ! fd.get('fontsize') )
            return this.querySelector('[name="fontsize"]').focus()

        fd.append( 'color', this.querySelector('[name="color"]').value.trim() )

        if ( ! fd.get('color') )
            return this.querySelector('[name="color"]').focus()

        fd.append( 'top_percent', parseFloat( this.querySelector('[name="top_percent"]').value ) )
        fd.append( 'font_family', this.querySelector('[name="font_family"]').value.trim() )

        template = this.querySelector('[name="template"]').files[0]

        if ( ! template || ! ( 'size' in template ) || template.size <= 0 )
            return this.querySelector('[name="template"]').focus()

        if ( ! /^image\//i.test( template.type ) )
            return alert( 'Invalid template file type.' )

        if ( template.size > SETTINGS.max_file_size )
            return alert( 'Max tempalte file size reached. Please upload files smaller than ' + (SETTINGS.max_file_size / 1000000).toFixed(2) + 'MB' )

        fd.delete('template')
        images_cont.innerHTML = ''

        file2base64(template, function(data)
        {
            fd.append('template', data)

            xhr = xhr || new XMLHttpRequest;

            if ( xhr.abort ) {
                xhr.abort()
            }

            xhr.open('POST', './xhr', true)

            xhr.onload = function()
            {
                if ( this.readyState == 4 && this.status == 200 ) {
                    try {var res=JSON.parse(this.response)} catch(e) {var res=this.response}
                    res = res || {}

                    if ( ! res.success ) {
                        alert( 'Error occurred:\n' + ( res.errors || ['Unknown error, please try again.'] ).join('\n') )
                        return
                    }

                    ( res.images || [] ).forEach(function(src)
                    {
                        var img = document.createElement('img')
                        img.src = src
                        images_cont.appendChild(img)
                    })
                }
            }

            xhr.send(fd)
        })
    })

    var file2base64 = function(file, then)
    {
       var reader = new FileReader()
       reader.readAsDataURL(file)
       reader.onload = function ()
       {
         then(reader.result)
       }
    }
})()