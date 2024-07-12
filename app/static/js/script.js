// app/static/js/script.js
"use strict";

const EPH_DATE_MIN = [-3000, 1, 29];  // 29 January 3001 BCE
const EPH_DATE_MAX = [3000, 5, 6];  // 6 May 3000 CE
const DATE_IDS = ['year', 'month', 'day', 'hour'];
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


/**
 * Formats the date and time into strings.
 *
 * @param {Number} year - 0 is 1 BCE
 * @param {Number} month - starts from 1, default is 1
 * @param {Number} day - default is 1
 * @param {Number} hour - 24-hour format, default is 12
 * @param {Number} minute - default is 0
 * @param {Number} second - default is 0
 * @returns {Array.<string>} An array containing two strings: the formatted date and the formatted time.
 */
function formatTime(year, month = 1, day = 1, hour = 12, minute = 0, second = 0) {
    const pad = number => number.toString().padStart(2, '0');
    const yearStr = year > 0 ? `${year} CE` : `${-year + 1} BCE`;
    const monthStr = MONTHS[month].abbr;
    const dateStr = `${day} ${monthStr} ${yearStr}`;
    const timeStr = `${pad(hour)}:${pad(minute)}:${pad(second)}`;
    return [dateStr, timeStr];
}


function clearForm() {
    DATE_IDS.forEach(id => {
        document.getElementById(id).value = '';
    });
    document.getElementById('results').innerHTML = '';
    document.getElementById('error').innerHTML = '';
    // disableNextInput('year', 1);
}


function populateMonthOptions() {
    const monthSelect = document.getElementById('month');
    MONTHS.slice(1).forEach((month, index) => {
        const option = document.createElement('option');
        option.value = index + 1;
        option.textContent = month.name;
        monthSelect.appendChild(option);
    });
}


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


function adjustDate() {
    const yearElement = document.getElementById('year');
    const monthElement = document.getElementById('month');
    const dayElement = document.getElementById('day');
    const year = parseInt(yearElement.value) || new Date().getFullYear();
    const month = parseInt(monthElement.value);

    if (month === 2) {
        dayElement.max = (year % 4 === 0 && (year % 100 !== 0 || year % 400 === 0)) ? 29 : 28;
    } else if ([4, 6, 9, 11].includes(month)) {
        dayElement.max = 30;
    } else {
        dayElement.max = 31;
    }

    Array.from(monthElement.options).forEach(option => {
        option.disabled = false;
    });

    let dayMin = 1;
    let dayMax = dayElement.max;
    if (year === EPH_DATE_MIN[0]) {
        /* Disable month options before EPH_DATE_MIN */
        Array.from(monthElement.options).forEach(option => {
            if (parseInt(option.value) < EPH_DATE_MIN[1]) {
                option.disabled = true;
            }
        });
        if (month < EPH_DATE_MIN[1]) {
            monthElement.value = EPH_DATE_MIN[1];
        } else if (month === EPH_DATE_MIN[1]) {
            dayMin = EPH_DATE_MIN[2];
        }
    } else if (year === EPH_DATE_MAX[0]) {
        /* Disable month options after EPH_DATE_MAX */
        Array.from(monthElement.options).forEach(option => {
            if (parseInt(option.value) > EPH_DATE_MAX[1]) {
                option.disabled = true;
            }
        });
        if (month > EPH_DATE_MAX[1]) {
            monthElement.value = EPH_DATE_MAX[1];
        } else if (month === EPH_DATE_MAX[1]) {
            dayMax = EPH_DATE_MAX[2];
        }
    }

    if (parseInt(dayElement.value) < dayMin) {
        dayElement.value = dayMin;
    }
    if (parseInt(dayElement.value) > dayMax) {
        dayElement.value = dayMax;
    }
}


async function handleFormSubmit(event) {
    event.preventDefault();
    const now = new Date();
    let   year   = parseInt(document.getElementById('year').value);
    let   month  = parseInt(document.getElementById('month').value)  || 1;
    let   day    = parseInt(document.getElementById('day').value)    || 1;
    const hour   = parseInt(document.getElementById('hour').value)   || 12;
    const minute = 0;
    const second = 0;
    
    if (!year && year !== 0) {
        year = now.getFullYear();
        month = now.getMonth() + 1;  // JavaScript months are 0-based
        day = now.getDate();
    }

    /* Validation for date */
    if ((year < EPH_DATE_MIN[0] ||
        (year === EPH_DATE_MIN[0] &&
            (month < EPH_DATE_MIN[1] ||
                (month === EPH_DATE_MIN[1] && day < EPH_DATE_MIN[2]))))
        ||
        (year > EPH_DATE_MAX[0] ||
        (year === EPH_DATE_MAX[0] &&
            (month > EPH_DATE_MAX[1] ||
                (month === EPH_DATE_MAX[1] && day > EPH_DATE_MAX[2]))))
    ) {
      document.getElementById("results").innerHTML = "";
      document.getElementById("error").innerHTML = `<p>Out of the ephemeris date range: ${formatTime(...EPH_DATE_MIN)[0]}&nbsp;\u2013&nbsp;${formatTime(...EPH_DATE_MAX)[0]}</p>`;
      return;
    }

    /* Display the current value */
    document.getElementById('year').value   = `${year}`;
    document.getElementById('month').value  = `${month}`;
    document.getElementById('day').value    = `${day}`;
    document.getElementById('hour').value   = `${hour}`;
    // document.getElementById('minute').value = `${minute}`;
    // document.getElementById('second').value = `${second}`;

    const apiUrl = `/coords?year=${year}&month=${month}&day=${day}&hour=${hour}&minute=${minute}&second=${second}`;

    try {
        const response = await fetch(apiUrl);
        const data = await response.json();

        if (data.error) {
            document.getElementById('results').innerHTML = '';
            document.getElementById('error').innerHTML = `<p>${data.error}</p>`;
        } else {
            const results = data.results;
            const datetimeStr = formatTime(
                ...[data.year, data.month, data.day, data.hour, data.minute, data.second]
                .map(v => parseInt(v))
            );
            const resultsHtml = `
                <h3>ICRS Coordinates (J2000) of Equinoxes and Solstices
                    on <span style="color: blue;">${datetimeStr[0]}</span>,
                    at <span style="color: blue;">${datetimeStr[1]}</span>:
                </h3>
                <table border="1" style="margin-left: auto; margin-right: auto;">
                    <tr>
                        <th></th>
                        <th>Right Ascension (RA)</th>
                        <th>Declination (Dec)</th>
                    </tr>
                    <tr>
                        <td>Vernal Equinox</td>
                        <td>${results.vernal_ra}</td>
                        <td>${results.vernal_dec}</td>
                    </tr>
                    <tr>
                        <td>Autumnal Equinox</td>
                        <td>${results.autumnal_ra}</td>
                        <td>${results.autumnal_dec}</td>
                    </tr>
                    <tr>
                        <td>Summer Solstice</td>
                        <td>${results.summer_ra}</td>
                        <td>${results.summer_dec}</td>
                    </tr>
                    <tr>
                        <td>Winter Solstice</td>
                        <td>${results.winter_ra}</td>
                        <td>${results.winter_dec}</td>
                    </tr>
                </table>
            `;
            document.getElementById('results').innerHTML = resultsHtml;
            document.getElementById('error').innerHTML = '';
        }
    } catch (error) {
        document.getElementById('error').innerHTML = `<p>There was an error processing your request.</p>`;
        document.getElementById('results').innerHTML = '';
    }
}


document.addEventListener('DOMContentLoaded', () => {
    populateMonthOptions();
    clearForm();

    /* Adjust the date */
    DATE_IDS.slice(0, 2).forEach(id => {
        document.getElementById(id).addEventListener('change', adjustDate);
    });

    // DATE_IDS.slice(0, 4).forEach((id, index) => {
    //     document.getElementById(id).addEventListener('change', function() {
    //         disableNextInput(id, index + 1);
    //         if (['year', 'month'].includes(id)) {adjustDate();}
    //     });
    // });
});
