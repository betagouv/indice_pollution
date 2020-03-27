<template>

<autocomplete
  :search="search"
  :get-result-value="getResultValue"
  @submit="onSubmit"
  placeholder="Recherchez une ville"
  aria-label="Recherchez une ville"
  ></autocomplete>

</template>

<script>
import Autocomplete from '@trevoreyre/autocomplete-vue'
import '@trevoreyre/autocomplete-vue/dist/style.css'
const apiUrl = '/autocomplete'

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
        onSubmit(result) {
          window.location = `/ville/${encodeURI(result.code)}`
        },
    }
}
</script>
