sudo -E sh -c "python topology_ref/mid_iid_ref.py;\
        mnf_clean;\
        python topology_ref/non_iid_ref.py"

echo end >> terminou.txt