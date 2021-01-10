<template>
    <div :class="{[$options.name]: true}">
        <site-button
                @click="onClickNote"
                :link-appearance="true"
        >
            <fa-icon :icon="['fas', 'sticky-note']" size="2x"></fa-icon>
        </site-button>
        <label id="name">{{name}}</label>

        <input-float
                :id="`${id}:amount`"
                label="Amount"
                :extra='{style:"min-width: 0;text-align: right"}'
                v-model="synced.amount"
                @input="$emit('update:amount', parseFloat(synced.amount))"
        ></input-float>
        <input-float
                :id="`${id}:unit`"
                type="select"
                label="Unit"
                v-model="synced.unit"
                @input="$emit('update:unit', synced.unit)"
                :hide-default-option="true"
        >
            <option value="weight">grams</option>
            <option value="servings">servings</option>
        </input-float>
        <site-button
                @click="$emit('delete')"
                :link-appearance="true"
        >
            <fa-icon :icon="['fas', 'minus']" size="2x"></fa-icon>
        </site-button>

        <input-float
                :id="`${id}:note`"
                class="note"
                label='Note'
                hint="Information about this specific ingredient in this specific recipe"
                :multiline="true"
                v-show="hasNote"
                :extra='{class:{"resizable-vertical":true}}'
                v-model="synced.note"
                @input="$emit('update:note', synced.note)"
        ></input-float>
    </div>
</template>

<script>
    import InputFloat from "@/components/inputs/input-float";
    import SiteButton from "@/components/inputs/site-button";

    export default {
        name: "recipe-component",
        components: {SiteButton, InputFloat},
        props: {
            name: String,
            note: String,
            unit: String, // one of 'servings' or 'weight'
            amount: Number,
            type: String,
            recipe_or_ingredient_id: Number,
            id: Number,
        },
        data() {
            return {
                // Internal data storage for user editable properties
                synced:{
                    note: '',
                    unit: null,
                    amount: null,
                },
                // If the user has stated they wanted to add a note
                wantsNote: false
            }
        },
        mounted(){
            // Transfer synced props to internal data
            this.synced.note = this.note || '';
            this.synced.unit = this.unit;
            this.synced.amount = this.amount;

            // Do this so that deleting the note text does not immediately hide the note box
            this.wantsNote = this.synced.note !== '';
        },
        computed: {
            hasNote() {
                return this.synced.note !== '' || this.wantsNote;
            }
        },
        methods:{
            onClickNote(){
                this.wantsNote = !this.wantsNote;
                this.note = ''
            }
        }
    }
</script>

<style>
    .recipe-component {
        display: contents;
    }
</style>