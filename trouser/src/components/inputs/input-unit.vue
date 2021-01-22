<!--
Creates an input with an adjustable unit as one single control. If conversion data is specified,
adjusting the unit will also automatically convert the input amount

While other inputs are more general, this one is limited to being a number to help in conversion.
You can still pass null to indicate no value
-->
<template>
    <div :class="$options.name">
        <label class="label" :for="id" v-if="label">{{label}}</label>
        <div>
            <input-float
                    class="amount"
                    :id="id"
                    v-model="displayValue"
                    input_mask_name="nutrition_mask"
                    @change="onChange"
            />
            <input-float
                    class="unit"
                    :id="`${id}:unit`"
                    type="select"
                    v-model="displayUnit"
            >
                <option v-for="unit in Object.keys(normalizedUnits)" :key="unit" :value="unit">{{unit}}</option>
            </input-float>
        </div>
    </div>
</template>

<script>
    import InputFloat from "@/components/inputs/input-float";

    export default {
        name: "input-unit",
        components: {InputFloat},
        props: {
            // The id to use for the inputs
            id: {
                type: String,
                required: true
            },
            // The label for this input
            label: {
                type: String
            },
            // Which unit of the units dictionary is the primary one. Any conversion data should specify how to convert
            // to this unit. (e.g. 'g'). No matter what unit is currently chosen by the user or displayed, the reported
            // value of this component will be in this unit.
            primaryUnit: {
                type: String,
                required: true
            },
            // Describe what units are available for this value.
            // If a string, then the unit will be set directly, and the user will have no control
            // If an array, the user will have the ability to pick from amoung the provided units, but no automatic conversion will happen
            // If an object, the keys should be units and the values should be ratios describing how many of the primary unit is in 1 of the given unit
            // E.g. {'g': 1, 'mg': 0.001, 'kg': 1000}
            // If not specified, then the primary unit will be considered as if passed as a string here.
            units: {
                type: [Object, Array, String],
                required: false
            },
            // The current value of this input. In primary units
            value: {
                type: Number,
                default: null
            }
        },
        data() {
            return {
                /**
                 * The currently displayed unit. Affects the display value
                 */
                displayUnit: this.primaryUnit,
                // Stores an intermediary string representation of the value, as we only emit an updated value
                // on change, but can update this value immediately. This value is stored in primary units, and does
                // not contain invalid trailing zeros
                // String
                internalValue: this.value,
                // If not null, the number of zeros to show in the input field. If 0, there will be a trailing decimal e.g. "1."
                trailingZeros: null
            }
        },
        computed: {
            displayValue: {
                /**
                 * The currently displayed value, based on the display unit. It can be a string so that trailing numbers can be input
                 * e.g. "1." and "1.0" are both invalid numbers, but necessary so that you can type "1.01"
                 * @returns {String}
                 */
                get() {
                    return this.convertUnitsString(this.internalValue, this.primaryUnit, this.displayUnit, this.trailingZeros);
                },
                set(value) {
                    // Update the number of trailing zeros we expect to display in the output
                    // They will be used when we convert the updated value back to be displayed
                    // Use regex to get the length of all trailing zeros
                    let match = value.match(/\.([0-9]*[1-9]+)*(?<trailingZeros>0+)$/);
                    if(match === null){
                        this.trailingZeros = 0; // May still have a trailing '.'
                    } else {
                        this.trailingZeros = match.groups.trailingZeros.length;
                    }
                    // If no trailing zeros, determine if we need a trailing decimal, or nothing at all
                    if(
                        (this.trailingZeros === 0 && value.indexOf(".") !== value.length - 1)
                        || value.length === 0
                    ) this.trailingZeros = null;

                    // The internal value does not contain trailing zeros, as it is supposed to be a string representation of a valid number
                    // So we always pass null
                    this.internalValue = this.convertUnitsString(value, this.displayUnit, this.primaryUnit, null);
                    // However we may still have a chance to update the real value, if there are no trailing zeroes
                    // If we did emit this and there were trailing zeros, the component would re-render and we would lose them
                    if(this.trailingZeros === null) this.$emit('input', parseFloat(value) || null);
                }
            },
            /**
             * Returns a units dictionary, even if the units passed in was an array or string
             * @returns {object}
             */
            normalizedUnits() {
                if (typeof this.units === 'string') return {[this.units]: 1};
                if (Array.isArray(this.units)) return this.units.reduce((output, unit) => {
                    output[unit] = 1;
                    return output
                }, {});
                return this.units;
            }
        },
        watch: {
            // If the display unit changes, we want to wipe out the trailing zeros
            displayUnit(){
                this.trailingZeros = null;
            }
        },
        methods: {
            /**
             * Converts the given value that is in inUnits, to a value that is in outUnits
             * @param {number} value The value given in inUnits
             * @param {string} inUnit The unit the value starts out in, must exist in the normalizedUnits dictionary
             * @param {string} outUnit The unit the return value is in, must exist in the normalizedUnits dictionary
             * @returns {number}
             */
            convertUnits(value, inUnit, outUnit) {
                // Get the ratio of the current unit
                var inRatio = this.normalizedUnits[inUnit];
                var outRatio = this.normalizedUnits[outUnit];
                return (value * inRatio) / outRatio
            },
            /**
             * Converts the given value that is in inUnits, to a value that is in outUnits.
             * Allows trailing decimals and 0's so that "1." and "1.0" could both be returned
             * @param {string} value The value given in inUnits
             * @param {string} inUnit The unit the value starts out in, must exist in the normalizedUnits dictionary
             * @param {string} outUnit The unit the return value is in, must exist in the normalizedUnits dictionary
             * @param {int} trailingZeros if not null, a decimal and this number of 0's will be appended. If 0, a trailing decimal will exist
             * @returns {string}
             */
            convertUnitsString(value, inUnit, outUnit, trailingZeros) {
                // Get the ratio of the current unit
                var inRatio = this.normalizedUnits[inUnit];
                var outRatio = this.normalizedUnits[outUnit];
                var val = ((parseFloat(value) * inRatio) / outRatio).toString();

                if (trailingZeros === 0){
                    val += ".";
                } else if (trailingZeros > 0){
                    val += "." + "0".repeat(trailingZeros);
                }
                return val;
            },
            onChange() {
                // Update the value prop on change
                this.$emit('input', parseFloat(this.internalValue) || null);
            }
        }
    }
</script>

<style scoped lang="scss">
    .input-unit {
        // Same as for float-input
        > .label {
            color: c(float-input, label);
            display: block;
            box-sizing: border-box;
            font-size: .8em;
            overflow: hidden;
            white-space: nowrap;
            text-overflow: ellipsis;
            padding: .5em 0.6rem;
            pointer-events: none;
            top: 0;
            text-align: left;
            transform: none;
            transition: all .2s ease-out;
            user-select: none;
            width: 100%;
            z-index: 1;
        }
        >div{
            display: flex;
            align-items: stretch;

            .amount {
                flex: 1;

                ::v-deep .field__input {
                    text-align: right;
                    border-top-right-radius: 0;
                    border-bottom-right-radius: 0;
                    border-right-width: 0;
                }
            }

            .unit {
                ::v-deep .field__input {
                    padding-left: 0;
                    appearance: none;
                    line-height: 1.2em; // Fix bottom of text getting cut off

                    border-top-left-radius: 0;
                    border-bottom-left-radius: 0;
                    border-left-width: 0;
                }
            }
        }
    }

</style>