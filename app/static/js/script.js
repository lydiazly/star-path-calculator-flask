// app/static/js/script.js
"use strict";

const EPH_DATE_MIN = [-3000, 1, 29];  // 29 January 3001 BCE (Gregorian)
const EPH_DATE_MAX = [3000, 5, 6];  // 6 May 3000 CE
const DATE_IDS = ['year'];
const MONTHS = [
    { abbr: '', name: '' },
    { abbr: 'Jan', name: 'January' },
    { abbr: 'Feb', name: 'February' },
    { abbr: 'Mar', name: 'March' },
    { abbr: 'Apr', name: 'April' },
    { abbr: 'May', name: 'May' },
    { abbr: 'Jun', name: 'June' },
    { abbr: 'Jul', name: 'July' },
    { abbr: 'Aug', name: 'August' },
    { abbr: 'Sep', name: 'September' },
    { abbr: 'Oct', name: 'October' },
    { abbr: 'Nov', name: 'November' },
    { abbr: 'Dec', name: 'December' }
];

const pad = number => number.toString().padStart(2, '0');

/**
 * Formats the datetime into strings in the format 'January 1, 2000 CE' and '12:00:00[.000]'.
 *
 * @param {Object} params - An object containing `year`, `month`, `day`, `hour`, `minute`, `second`, and some switches.
 * @param {number} params.year - Year. 0 is 1 BCE.
 * @param {number} [params.month=1] - Month. Starts from 1. Defaults to `1` (January).
 * @param {number} [params.day=1] - Day of the month. Defaults to `1`.
 * @param {number} [params.hour=12] - Hours in 24-hour format. Defaults to `12`.
 * @param {number} [params.minute=0] - Minutes. Defaults to `0`.
 * @param {number} [params.second=0] - Seconds (integer or float). Defaults to `0`.
 * @param {boolean} [params.monthFirst=true] - Whether to use month-day-year instead of day-month-year format. Defaults to `true`.
 * @param {boolean} [params.abbr=false] - Whether to use abbreviation instead of full name for month. Defaults to `false`.
 * @returns {Object} An object containing three formatted strings: full `date`, `time`, and the `year` only.
 */
const formatDateTime = ({ year, month = 1, day = 1, hour = 12, minute = 0, second = 0,
                          monthFirst = true, abbr = false }) => {
  const yearStr = year > 0 ? `${year} CE` : `${-year + 1} BCE`;
  const monthStr = MONTHS[month][abbr ? 'abbr' : 'name'];
  const dateStr = monthFirst
    ? `${monthStr} ${day}, ${yearStr}`
    : `${day} ${monthStr} ${yearStr}`;
  const secondStr = Number.isInteger(second) ? pad(second) : second.toFixed(3).padStart(6, '0');
//   const secondStr = second.toFixed().padStart(2, '0');
  const timeStr = `${pad(hour)}:${pad(minute)}:${secondStr}`;
  return { date: dateStr, time: timeStr, year: yearStr };
};

/**
 * Formats the datetime into ISO 8601 format strings '+2000-01-01' and '12:00:00[.000]'
 *
 * @param {Object} params - An object containing `year`, `month`, `day`, `hour`, `minute`, and `second`.
 * @param {number} params.year - Year. 0 is 1 BCE.
 * @param {number} [params.month=1] - Month. Starts from 1. Defaults to `1` (January).
 * @param {number} [params.day=1] - Day of the month. Defaults to `1`.
 * @param {number} [params.hour=12] - Hours in 24-hour format. Defaults to `12`.
 * @param {number} [params.minute=0] - Minutes. Defaults to `0`.
 * @param {number} [params.second=0] - Seconds (integer or float). Defaults to `0`.
 * @returns {Object} An object containing two formatted strings: `date` and `time`.
 */
const formatDateTimeISO = ({ year, month = 1, day = 1, hour = 12, minute = 0, second = 0 }) => {
  const yearStr = year >= 0 ? '+' + year.toString().padStart(4, '0') : '-' + (-year).toString().padStart(4, '0');
  const dateStr = [yearStr, pad(month), pad(day)].join('-');
  const secondStr = Number.isInteger(second) ? pad(second) : second.toFixed(3).padStart(6, '0');
//   const secondStr = second.toFixed().padStart(2, '0');
  const timeStr = `${pad(hour)}:${pad(minute)}:${secondStr}`;
  return { date: dateStr, time: timeStr };
};

/**
 * Formats a datetime array into a string.
 * Calls `formatDateTimeISO` or `formatDateTime` to format the date and time. Then joins them.
 *
 * @param {Object} params - An object containing a datetime array and some switches.
 * @param {number[]} params.dateTime - An array [year, month, day, hour, minute, second].
 * @param {boolean} [params.iso=true] - Whether to use ISO format or not. Defaults to `true`.
 * @param {string} [params.delim=' '] - Delimiter between date and time in ISO format. Defaults to `' '`.
 * @param {boolean} [params.monthFirst=true] - Whether to use month-day-year instead of day-month-year format. Defaults to `true`.
 * @param {boolean} [params.abbr=false] - Whether to use abbreviation or full name for month. Defaults to `false`.
 * @returns {string} The formatted date and time string.
 *
 * @see formatDateTimeISO
 * @see formatDateTime
 */
const dateTimeToStr = ({ dateTime, iso = true, delim = ' ', monthFirst = true, abbr = false }) => {
  if (!Array.isArray(dateTime) || dateTime.length < 6) return '';

  const [year, month, day, hour, minute, second] = dateTime.map((value, index) => {
    if (index === 5) return parseFloat(value);  // Parse the second as float
    return parseInt(value);  // Parse other values as int
  });

  const dateTimeStrList = iso
    ? formatDateTimeISO({ year, month, day, hour, minute, second })
    : formatDateTime({ year, month, day, hour, minute, second, monthFirst, abbr });
  const dateTimeStr = iso
    ? `${dateTimeStrList.date}${delim}${dateTimeStrList.time}`
    : `${dateTimeStrList.date}, ${dateTimeStrList.time}`;
  return dateTimeStr;
};

function clearForm() {
    DATE_IDS.forEach(id => {
        document.getElementById(id).value = '';
    });
    document.getElementById('results').innerHTML = '';
    document.getElementById('error').innerHTML = '';
    // disableNextInput('year', 1);
}

// function populateMonthOptions() {
//     const monthSelect = document.getElementById('month');
//     MONTHS.slice(1).forEach((month, index) => {
//         const option = document.createElement('option');
//         option.value = index + 1;
//         option.textContent = month.name;
//         monthSelect.appendChild(option);
//     });
// }

// function disableNextInput(thisId, nextIndex) {
//     const thisValue = document.getElementById(thisId).value;
//     console.log(`${thisId} is empty: ${!thisValue && parseInt(thisValue)}`)
//     if (!thisValue && parseInt(thisValue) != 0) {
//         DATE_IDS.slice(nextIndex).forEach(id => {
//             document.getElementById(id).value = '';
//             document.getElementById(id).disabled = true;
//             console.log(`${id}.disabled = ${document.getElementById(id).disabled}`);
//         });
//     } else {
//         document.getElementById(DATE_IDS[nextIndex]).disabled = false;
//         console.log(`${DATE_IDS[nextIndex]}.disabled = ${document.getElementById(DATE_IDS[nextIndex]).disabled}`);
//     }
// }

// function adjustDate() {
//     const yearElement = document.getElementById('year');
//     const monthElement = document.getElementById('month');
//     const dayElement = document.getElementById('day');
//     const year = parseInt(yearElement.value) || new Date().getFullYear();
//     const month = parseInt(monthElement.value);

//     if (month === 2) {
//         dayElement.max = (year % 4 === 0 && (year % 100 !== 0 || year % 400 === 0)) ? 29 : 28;
//     } else if ([4, 6, 9, 11].includes(month)) {
//         dayElement.max = 30;
//     } else {
//         dayElement.max = 31;
//     }

//     Array.from(monthElement.options).forEach(option => {
//         option.disabled = false;
//     });

//     let dayMin = 1;
//     let dayMax = dayElement.max;
//     if (year === EPH_DATE_MIN[0]) {
//         /* Disable month options before EPH_DATE_MIN */
//         Array.from(monthElement.options).forEach(option => {
//             if (parseInt(option.value) < EPH_DATE_MIN[1]) {
//                 option.disabled = true;
//             }
//         });
//         if (month < EPH_DATE_MIN[1]) {
//             monthElement.value = EPH_DATE_MIN[1];
//         } else if (month === EPH_DATE_MIN[1]) {
//             dayMin = EPH_DATE_MIN[2];
//         }
//     } else if (year === EPH_DATE_MAX[0]) {
//         /* Disable month options after EPH_DATE_MAX */
//         Array.from(monthElement.options).forEach(option => {
//             if (parseInt(option.value) > EPH_DATE_MAX[1]) {
//                 option.disabled = true;
//             }
//         });
//         if (month > EPH_DATE_MAX[1]) {
//             monthElement.value = EPH_DATE_MAX[1];
//         } else if (month === EPH_DATE_MAX[1]) {
//             dayMax = EPH_DATE_MAX[2];
//         }
//     }

//     if (parseInt(dayElement.value) < dayMin) {
//         dayElement.value = dayMin;
//     }
//     if (parseInt(dayElement.value) > dayMax) {
//         dayElement.value = dayMax;
//     }
// }

async function handleFormSubmit(event) {
    event.preventDefault();
    const now = new Date();
    let   year   = parseInt(document.getElementById('year').value);
    // let   month  = parseInt(document.getElementById('month').value)  || 1;
    // let   day    = parseInt(document.getElementById('day').value)    || 1;
    // const hour   = parseInt(document.getElementById('hour').value)   || 12;
    // const minute = 0;
    // const second = 0;

    if (!year && year !== 0) {
        year = now.getFullYear();
        // month = now.getMonth() + 1;  // JavaScript months are 0-based
        // day = now.getDate();
    }

    /* Validation for date */
    if (year <= EPH_DATE_MIN[0] || year >= EPH_DATE_MAX[0]) {
      document.getElementById("results").innerHTML = "";
      document.getElementById("error").innerHTML = `<p>Out of the year range: ${EPH_DATE_MIN[0]+1}/+${EPH_DATE_MAX[0]-1}</p>`;
      return;
    }

    /* Display the current value */
    document.getElementById('year').value   = `${year}`;

    const apiUrl = `/seasons?tz=Etc%2FGMT&year=${year}`;

    try {
        const response = await fetch(apiUrl);
        const data = await response.json();

        if (data.error) {
            document.getElementById('results').innerHTML = '';
            document.getElementById('error').innerHTML = `<p>${data.error}</p>`;
        } else {
            const results = data.results;
            // const datetimeStr = formatDateTime(
            //     ...[data.year, data.month, data.day, data.hour, data.minute, data.second]
            //     .map(v => parseInt(v))
            // );
            const yearStr = formatDateTime({ year: data.year}).year;
            const resultsHtml = `
                <h3>The Equinoxes and Solstices in <span style="color: blue;">${year} (${yearStr})</span>:</h3>
                <table border="1" style="margin-left: auto; margin-right: auto;">
                    <tr>
                        <th></th>
                        <th>Date & Time (UT1)</th>
                        <th>Right Ascension (RA)</th>
                        <th>Declination (Dec)</th>
                    </tr>
                    <tr>
                        <td>Vernal Equinox</td>
                        <td>${dateTimeToStr({ dateTime: results.vernal_time })}</td>
                        <td>${results.vernal_ra.toFixed(3)}</td>
                        <td>${results.vernal_dec.toFixed(3)}</td>
                    </tr>
                    <tr>
                        <td>Summer Solstice</td>
                        <td>${dateTimeToStr({ dateTime: results.summer_time })}</td>
                        <td>${results.summer_ra.toFixed(3)}</td>
                        <td>${results.summer_dec.toFixed(3)}</td>
                    </tr>
                    <tr>
                        <td>Autumnal Equinox</td>
                        <td>${dateTimeToStr({ dateTime: results.autumnal_time })}</td>
                        <td>${results.autumnal_ra.toFixed(3)}</td>
                        <td>${results.autumnal_dec.toFixed(3)}</td>
                    </tr>
                    <tr>
                        <td>Winter Solstice</td>
                        <td>${dateTimeToStr({ dateTime: results.winter_time })}</td>
                        <td>${results.winter_ra.toFixed(3)}</td>
                        <td>${results.winter_dec.toFixed(3)}</td>
                    </tr>
                </table>
            `;
            document.getElementById('results').innerHTML = resultsHtml;
            document.getElementById('error').innerHTML = '';
        }
    } catch (error) {
        document.getElementById('error').innerHTML = `<p>There was an error processing your request: ${error}</p>`;
        document.getElementById('results').innerHTML = '';
    }
}

document.addEventListener('DOMContentLoaded', () => {
    // populateMonthOptions();
    clearForm();

    /* Adjust the date */
    // DATE_IDS.slice(0, 2).forEach(id => {
    //     document.getElementById(id).addEventListener('change', adjustDate);
    // });

    // DATE_IDS.slice(0, 4).forEach((id, index) => {
    //     document.getElementById(id).addEventListener('change', function() {
    //         disableNextInput(id, index + 1);
    //         if (['year', 'month'].includes(id)) {adjustDate();}
    //     });
    // });
});
