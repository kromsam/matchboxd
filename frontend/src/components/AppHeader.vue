<template>
  <div class="block has-text-centered">
    <h1 class="title is-2">
      Films in
      <div class="select is-medium is-primary is-inline-block">
        <select 
          v-model="currentCity"
          @change="$emit('updateCity', $event.target.value)"
        >
          <option v-for="city in cities" :key="city" :value="city">
            {{ city }}
          </option>
        </select>
      </div>
      van 
      <a :href="letterboxdUrl" 
         class="has-text-primary"
         target="_blank">{{ letterboxdList }}</a>
      <button class="button is-ghost is-medium" 
              @click.prevent="$emit('toggleSort')">
        {{ sortMode === 'film' ? 'per film' : 'op datum' }}
      </button>
    </h1>
  </div>
</template>

<script>
export default {
  props: ['letterboxdList', 'selectedCity', 'cities', 'sortMode'],
  computed: {
    letterboxdUrl() {
      return `https://letterboxd.com/${this.letterboxdList}`
    },
    currentCity: {
      get() { return this.selectedCity },
      set(value) { this.$emit('updateCity', value) }
    }
  }
}
</script>