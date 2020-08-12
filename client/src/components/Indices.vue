<template>
    <div class="section">
        <h1>Indice de pollution à {{ nomVille }}</h1>
        <div class="tiles">
            <div class="grid">
                <Indice 
                    v-for="(indice, index) in indices"
                    v-bind:indice="indice.indice"
                    v-bind:date="indice.date"
                    v-bind:index="index"
                    v-bind:key="indice.date"
                >
                </Indice>

            </div>
        </div>
    </div>
</template>
<script>
import Indice from './Indice.vue'
export default {
    name: 'Indices',
    components: {Indice},
    data: function() {
        return {
            indices: [],
            nomVille: ""
        }
    },
    props: ['insee'],
    created: function() {
        this.fetchData()
    },
    methods: {
        fetchData() {
            fetch(`/forecast?insee=${this.insee}`)
                .then(response => response.json())
                .then(data => {
                    this.indices = data.data
                })

            fetch(`https://geo.api.gouv.fr/communes/${this.insee}?fields=nom&format=json&geometry=centre`)
                .then(response => response.json())
                .then(data => {
                    this.nomVille = data['nom']
                })

        }
    },
}
</script>