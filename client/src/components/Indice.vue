<template>
    <div class="tile" :class="classObject" >
        <h3>{{ date }}</h3>
        <h2>{{ indice }}</h2>
        <span> {{ indice_label[indice] }}</span>
    </div>
</template>
<script>
export default {
    name: 'Indice',
    props: ['date', 'indice'],
    data() {
        return {
            indice_class: {
                1: "tresbon",
                2: "tresbon",
                3: "bon",
                4: "bon",
                5: "moyen",
                6: "mediocre",
                7: "mediocre",
                8: "mauvais",
                9: "mauvais",
                10: "tresmauvais"
            },
            indice_label: {
                1: "Très bon",
                2: "Très bon",
                3: "Bon",
                4: "Bon",
                5: "Moyen",
                6: "Mediocre",
                7: "Mediocre",
                8: "Mauvais",
                9: "Mauvais",
                10: "Très mauvais"

            }
        }
    },
    computed: {
        classObject: function() {
            console.log(this)
            console.log(this.indice_class)
            console.log(this.indice)
            console.log(this.indice_class[this.indice])
            return this.indice_class[this.indice]
        }
    }
}
</script>
<style>
.bon {
    background-color: #daf5e7 ;
}
.tresbon {
    background-color: #daf5e7 ;
}

.moyen {
    background-color: #fff0e4 ;
}
.mediocre {
    background-color: #fff0e4 ;
}

.mauvais {
    background-color: #efaca6 ;
}
.tresmauvais {
    background-color: #efaca6 ;
}
</style>