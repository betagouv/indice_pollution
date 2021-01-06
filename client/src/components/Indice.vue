<template>
    <div class="tile" v-bind:style="{background: couleur}">
        <h3>{{ date }}</h3>
        <h2>{{ label }}</h2>
    </div>
</template>
<script>
export default {
    name: 'Indice',
    props: ['date', 'label', 'couleur'],
}
</script>