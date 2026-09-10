
// pages/DetailsPage.js
import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';

function DetailsPage() {
  const { id } = useParams();
  const [item, setItem] = useState(null);
  const [errorMessage, setErrorMessage] = useState(null);

  useEffect(() => {
    fetchItemDetails();
  }, [id]);

  const fetchItemDetails = async () => {

    try {
      const url =process.env.REACT_APP_API_SERVER_URL + 'Documents/' + id + '/prediction';

      const response = await fetch(url);
      const data = await response.json();
      if (response.ok) {

        setItem(data);
      }
      else
        throw new Error(data.error);

    } catch (error) {
      console.log(error.message);
      setErrorMessage(error.message);

    }
  };
  if (errorMessage) {

    return (
      <div className="flex items-center p-4 mb-4 text-sm text-red-800 border border-red-300 rounded-lg bg-red-50 dark:bg-gray-800 dark:text-red-400 dark:border-red-800" role="alert">
        <svg className="flex-shrink-0 inline w-4 h-4 me-3" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="currentColor" viewBox="0 0 20 20">
          <path d="M10 .5a9.5 9.5 0 1 0 9.5 9.5A9.51 9.51 0 0 0 10 .5ZM9.5 4a1.5 1.5 0 1 1 0 3 1.5 1.5 0 0 1 0-3ZM12 15H8a1 1 0 0 1 0-2h1v-3H8a1 1 0 0 1 0-2h2a1 1 0 0 1 1 1v4h1a1 1 0 0 1 0 2Z" />
        </svg>
        <span className="sr-only">Info</span>
        <div>
          <span className="font-medium">Error!</span> Something went wrong - {errorMessage}.
        </div>
      </div>);
  }

  if (!item) {

    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-lg font-semibold">Loading...</div>
      </div>
    );
  }
  else {
    return (
      <div className="px-40 flex flex-1 justify-center py-5">
        <div className="layout-content-container flex flex-col w-[512px] max-w-[512px] py-5 max-w-[960px] flex-1">
          <div className="flex flex-wrap justify-between gap-3 p-4">
            <p className="text-[#141C24] tracking-light text-[32px] font-bold leading-tight min-w-72">Invoice: {item.invoice.invoice_number}</p></div>
          <h3 className="text-[#141C24] text-lg font-bold leading-tight tracking-[-0.015em] px-4 pb-2 pt-4">Approval Prediction</h3>

          <p className="text-[#3F5374] text-sm font-normal leading-normal pb-3 pt-1 px-4">Predicted approval:
            <span style={{ backgroundColor: item.prediction.name == "Accepted" ? "green" : "red", color: "white" }}>{item.prediction.name + " with probability " + item.prediction.percent + "%"}</span></p>

          <div className="flex w-full grow bg-[#F8F9FB] @container p-4">
            <div className="w-full gap-1 overflow-scroll bg-[#F8F9FB] @[480px]:gap-2 aspect-[2/3] rounded-xl flex">
              <div
                className="w-full bg-center bg-no-repeat bg-cover aspect-auto rounded-none flex-1">
                 {item.file_paths.map((l) => (
                  <div>
                   <img src={l} />
                   <br></br>
                   </div>
                  ))}
                
                
              </div>
            </div>
          </div>
          <h3 className="text-[#141C24] text-lg font-bold leading-tight tracking-[-0.015em] px-4 pb-2 pt-4">Invoice Data Extraction</h3>
          <div className="p-4 grid grid-cols-2">
            <div className="flex flex-col gap-1 border-t border-solid border-t-[#D4DBE8] py-4 pr-2">
              <p className="text-[#3F5374] text-sm font-normal leading-normal">Vendor</p>
              <p className="text-[#141C24] text-sm font-normal leading-normal">{item.invoice.vendor}</p>
            </div>
            <div className="flex flex-col gap-1 border-t border-solid border-t-[#D4DBE8] py-4 pl-2">
              <p className="text-[#3F5374] text-sm font-normal leading-normal">Invoice date</p>
              <p className="text-[#141C24] text-sm font-normal leading-normal">{item.invoice.invoice_date}</p>
            </div>
            <div className="flex flex-col gap-1 border-t border-solid border-t-[#D4DBE8] py-4 pr-2">
              <p className="text-[#3F5374] text-sm font-normal leading-normal">Invoice due date</p>
              <p className="text-[#141C24] text-sm font-normal leading-normal">{item.invoice.invoice_due_date}</p>
            </div>
            <div className="flex flex-col gap-1 border-t border-solid border-t-[#D4DBE8] py-4 pl-2">
              <p className="text-[#3F5374] text-sm font-normal leading-normal">Po Number</p>
              <p className="text-[#141C24] text-sm font-normal leading-normal">{item.invoice.purchase_order_number}</p>
            </div>
            <div className="flex flex-col gap-1 border-t border-solid border-t-[#D4DBE8] py-4 pr-2">
              <p className="text-[#3F5374] text-sm font-normal leading-normal">Vendor Address</p>
              <p className="text-[#141C24] text-sm font-normal leading-normal">{item.invoice.vendor_address}</p>
            </div>
            <div className="flex flex-col gap-1 border-t border-solid border-t-[#D4DBE8] py-4 pl-2">
              <p className="text-[#3F5374] text-sm font-normal leading-normal">Subtotal</p>
              <p className="text-[#141C24] text-sm font-normal leading-normal">${item.invoice.items_subtotal}</p>
            </div>
            <div className="flex flex-col gap-1 border-t border-solid border-t-[#D4DBE8] py-4 pr-2">
              <p className="text-[#3F5374] text-sm font-normal leading-normal">HST</p>
              <p className="text-[#141C24] text-sm font-normal leading-normal">${item.invoice.invoice_tx}</p>
            </div>
            <div className="flex flex-col gap-1 border-t border-solid border-t-[#D4DBE8] py-4 pl-2">
              <p className="text-[#3F5374] text-sm font-normal leading-normal">Total</p>
              <p className="text-[#141C24] text-sm font-normal leading-normal">${item.invoice.invoice_total}</p>
            </div>
          </div>
          <h3 className="text-[#141C24] text-lg font-bold leading-tight tracking-[-0.015em] px-4 pb-2 pt-4">Line Items</h3>
          <div className="px-4 py-3 @container">
            <div className="flex overflow-hidden rounded-xl border border-[#D4DBE8] bg-[#F8F9FB]">
              <table className="flex-1">
                <thead>
                  <tr className="bg-[#F8F9FB]">

                    <th className="table-ea583f38-0fbe-4546-92ea-4542e2672e6b-column-240 px-4 py-3 text-left text-[#141C24] w-[400px] text-sm font-medium leading-normal">
                      Description
                    </th>
                    <th className="table-ea583f38-0fbe-4546-92ea-4542e2672e6b-column-360 px-4 py-3 text-left text-[#141C24] w-[400px] text-sm font-medium leading-normal">
                      Quantity
                    </th>
                    <th className="table-ea583f38-0fbe-4546-92ea-4542e2672e6b-column-480 px-4 py-3 text-left text-[#141C24] w-[400px] text-sm font-medium leading-normal">
                      Unit Price
                    </th>
                    <th className="table-ea583f38-0fbe-4546-92ea-4542e2672e6b-column-600 px-4 py-3 text-left text-[#141C24] w-[400px] text-sm font-medium leading-normal">
                      Total Price
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {item.invoice.invoice_items.map((l) => (
                    <tr className="border-t border-t-[#D4DBE8]" key={l.item_Description}>
                      <td className="table-ea583f38-0fbe-4546-92ea-4542e2672e6b-column-240 h-[72px] px-4 py-2 w-[400px] text-[#3F5374] text-sm font-normal leading-normal">
                        {l.item_Description}
                      </td>
                      <td className="table-ea583f38-0fbe-4546-92ea-4542e2672e6b-column-360 h-[72px] px-4 py-2 w-[400px] text-[#3F5374] text-sm font-normal leading-normal">{l.quantity}</td>
                      <td className="table-ea583f38-0fbe-4546-92ea-4542e2672e6b-column-480 h-[72px] px-4 py-2 w-[400px] text-[#3F5374] text-sm font-normal leading-normal">${l.unit_price}</td>
                      <td className="table-ea583f38-0fbe-4546-92ea-4542e2672e6b-column-600 h-[72px] px-4 py-2 w-[400px] text-[#3F5374] text-sm font-normal leading-normal">${l.item_total}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

          </div>


        </div>
      </div>
    );
  }
}

export default DetailsPage;