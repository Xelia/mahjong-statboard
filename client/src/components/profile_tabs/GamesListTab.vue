<template>
  <b-table
    :data="games"
    :narrowed="true"
    :mobileCards="false"
    :paginated="true"
    :per-page="10"
    :loading="loading"
  >
    <template slot-scope="props">
      <b-table-column label="Дата">
        {{ props.row.date }}
      </b-table-column>
      <b-table-column label="Игра">
        {{ props.row.results.map(r => `${r.player}:${r.score}`).join(', ') }}
      </b-table-column>
      <b-table-column label="Место">
        {{ props.row.results.filter(r => r.player == player.name)[0].place }}
      </b-table-column>
    </template>
  </b-table>
</template>

<script>
  import axios from 'axios'
  export default {
    props: ['player'],
    data() {
      return {
        games: [],
        loading: false
      }
    },
    mounted(){
      this.fetchData()
    },
    watch:{
      'player': 'fetchData'
    },
    methods: {
      async fetchData() {
        this.loading = true
        let res = await axios.get(`/api/instances/${this.$store.state.instance.id}/games/?format=json&player=${this.player.name}`)
        this.games = res.data
        this.loading = false
      },
    }
  }
</script>
