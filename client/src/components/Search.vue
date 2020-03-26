<template>

<autocomplete
  :search="search"
  :get-result-value="getResultValue"
  ></autocomplete>

</template>

<script>
import Autocomplete from '@trevoreyre/autocomplete-vue'
import '@trevoreyre/autocomplete-vue/dist/style.css'
const apiUrl = 'http://localhost:5000/autocomplete'

export default {
    name: 'Search',
    components: {
        Autocomplete
    },
    methods: {
        search(input) {
            const url = `${apiUrl}?q=${encodeURI(input)}`
            return new Promise(resolve => {
                if (input.length < 3) {
                  return resolve([])
                }

                fetch(url)
                  .then(response => response.json())
                  .then(data => {
                    resolve(data)
                  })

            }
            )
        },
        getResultValue(result) {
          return result.nom
        },
    }
}
</script>
