<template>
    <b-table
      :data="games"
      :striped="true"
      :narrowed="true"
      :mobileCards="true"
    >
      <template slot-scope="props">
        <b-table-column :visible="withDates" field="date" label="Дата">
            {{ props.row.date }}
        </b-table-column>
        <b-table-column field="date" label="Игрок1">
            {{ props.row.results[0].player }}
        </b-table-column>
        <b-table-column field="asfasf" label="Счет1">
            {{ props.row.results[0].score }}
        </b-table-column>
        <b-table-column field="date" label="Игрок2">
            {{ props.row.results[1].player }}
        </b-table-column>
        <b-table-column field="results[1].score" label="Счет2">
            {{ props.row.results[1].score }}
        </b-table-column>
        <b-table-column field="date" label="Игрок3">
            {{ props.row.results[2].player }}
        </b-table-column>
        <b-table-column field="date" label="Счет3">
            {{ props.row.results[2].score }}
        </b-table-column>
        <b-table-column field="date" label="Игрок4">
            {{ props.row.results[3].player }}
        </b-table-column>
        <b-table-column field="date" label="Счет4">
            {{ props.row.results[3].score }}
        </b-table-column>
      </template>
      <div slot="empty">qwe</div>
    </b-table>
</template>

<script>
export default {
  props: {
    games: Array,
    withDates: {type: Boolean, default: false}
  }
}
</script>

