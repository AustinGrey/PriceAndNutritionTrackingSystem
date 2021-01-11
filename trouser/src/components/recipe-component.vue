<template>
    <div :class="{[$options.name]: true}">
        <site-button
                @click.native="onClickNote"
                :link-appearance="true"
        >
            <fa-icon :icon="['fas', 'sticky-note']" size="2x"></fa-icon>
        </site-button>
        <label id="name">{{name}}</label>

        <input-float
                :id="`${id}:amount`"
                label="Amount"
                :extra='{style:"min-width: 0;text-align: right"}'
                v-model="syncedAmount"
        />
        <input-float
                :id="`${id}:unit`"
                type="select"
                label="Unit"
                v-model="syncedUnit"
                :hide-default-option="true"
        >
            <option value="weight">grams</option>
            <option value="servings">servings</option>
        </input-float>
        <site-button
                @click.native="$emit('delete')"
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
                v-model="syncedNote"
        />
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
                    unit: null,
                    amount: null,
                },
                // If the user has stated they wanted to add a note
                wantsNote: false
            }
        },
        mounted(){
            // Transfer synced props to internal data
            this.syncedNote = this.note || ''; //@todo is this necessary anymore?

            // Do this so that deleting the note text does not immediately hide the note box
            this.wantsNote = this.syncedNote !== '';
        },
        computed: {
            hasNote() {
                return this.syncedNote !== '' || this.wantsNote;
            },
            syncedNote:{
                get(){
                    return this.note;
                },
                set(value){
                    this.$emit("update:note", value);
                }
            },
            syncedUnit:{
                get(){
                    return this.unit;
                },
                set(value){
                    this.$emit("update:unit", value)
                }
            },
            syncedAmount:{
                get(){
                    return this.amount;
                },
                set(value){
                    this.$emit("update:amount", parseFloat(value))
                }
            }
        },
        methods:{
            onClickNote(){
                this.wantsNote = !this.wantsNote;
                this.syncedNote = '';

            }
        }
    }
</script>

<style>
    .recipe-component {
        display: contents;
    }
</style>