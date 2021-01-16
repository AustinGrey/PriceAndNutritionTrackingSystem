<template>
    <div :class="$options.name">
        <site-button
                @click.native="$emit('delete')"
                :link-appearance="true"
                class="delete"
        >
            <fa-icon :icon="['fas', 'minus']"></fa-icon>
        </site-button>
        <site-button
                :id="`${id}:name`"
                @click.native="onClickNote"
                :link-appearance="true"
                class="name"
        >
            {{name}}<span v-show="wantsNote">*</span>
        </site-button>
        <input-float
                :id="`${id}:amount`"
                class="amount"
                :label='includeLabels ? "Amount" : ""'
                :extra='{style:"min-width: 0;text-align: right"}'
                v-model="syncedAmount"
        />
        <input-float
                :id="`${id}:unit`"
                class="unit"
                type="select"
                :label='includeLabels ? "Unit" : ""'
                v-model="syncedUnit"
                :hide-default-option="true"
        >
            <option value="weight">g</option>
            <option value="servings">serving</option>
        </input-float>

        <input-float
                :id="`${id}:note`"
                class="note"
                :label='includeLabels ? "Note" : ""'
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
            note: {
                type:String,
                default: ''
            },
            unit: String, // one of 'servings' or 'weight'
            amount: Number,
            type: String,
            recipe_or_ingredient_id: Number,
            id: Number,
            includeLabels: {
                type: Boolean,
                default: true
            }
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
                    this.$emit("update:amount", parseFloat(value) || 0)
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

<style scoped lang="scss">
    .recipe-component {
        display: contents;
        .amount ::v-deep .field__input{
            border-top-right-radius: 0;
            border-bottom-right-radius: 0;
            border-right-color: transparent;
        }
        .unit ::v-deep .field__input{
            border-top-left-radius: 0;
            border-bottom-left-radius: 0;
            border-left-style: dashed;
            border-left-color: lightgrey;
        }
    }
</style>