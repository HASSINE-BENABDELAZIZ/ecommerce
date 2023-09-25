import React from 'react';
import Thead from './/Thead'
import Tbody from './/Tbody'
import Pagination from "./Pagination";
import ReactPaginate from "react-paginate";


const Table = (props) => {
    return (
        <div className="card mb-3">
            <div className="card-header">
                <div className="row flex-between-center">
                    <div className="col-4 col-sm-auto d-flex align-items-center pe-0">
                        <h5 className="fs-0 mb-0 text-nowrap py-2 py-xl-0">Orders</h5>
                    </div>
                    <div className="col-8 col-sm-auto ms-auto text-end ps-0">
                        <div id="orders-actions">
                            <a href="/order/create/" className="btn btn-falcon-default btn-sm"><span
                                className="fas fa-plus" data-fa-transform="shrink-3 down-2"></span><span
                                className="d-none d-sm-inline-block ms-1">Nouveau</span></a>
                            <a className="btn btn-falcon-default btn-sm mx-2" href="/order/logs/"><span
                                className="fas fa-filter" data-fa-transform="shrink-3 down-2"></span><span
                                className="d-none d-sm-inline-block ms-1">Journaux</span></a>


                            <a href="/order/import_files/" className="btn btn-falcon-default btn-sm">
                                <span className="fas fa-upload " data-fa-transform="shrink-3 down-2"></span><span
                                className="d-none d-sm-inline-block ms-1">csv</span>
                            </a>
                        </div>
                    </div>
                </div>
            </div>
            <div className="card-body p-0">
                <div className="table-responsive scrollbar" id="add_message">
                    <div id="content">

                        <table className="table table-bordered table-striped fs--1 mb-0"
                               id="selectable_table">
                            <Thead/>
                            <tbody id="select_all_items" className="list">

                            <Tbody orders={props.orders} />
                            </tbody>
                        </table><br />

                    </div>
                </div>
            </div>

        </div>

    )
}

export default Table
