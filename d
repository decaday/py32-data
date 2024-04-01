#!/bin/bash

set -ex

cd $(dirname $0)

CMD=$1
shift

case "$CMD" in
    download-all)
        echo TODO $CMD
    ;;
    install-chiptool)
        cargo install --git https://github.com/embassy-rs/chiptool
    ;;
    extract-all)
        peri=$1
        shift
        echo $@

        rm -rf tmp/$peri
        mkdir -p tmp/$peri

        for f in `ls svd/PY32*`; do
            echo $f
            svd_path=$f
            f=${f#"svd/PY32"}
            f=${f%"xx.svd"}
            echo -n processing $f ...
            if test -f  transforms/$peri.yaml; then
                trans_args="--transform transforms/$peri.yaml"
            fi

            if chiptool extract-peripheral $trans_args --svd $svd_path --peripheral $peri $@ > tmp/$peri/$f.yaml 2> tmp/$peri/$f.err; then
                rm tmp/$peri/$f.err
                echo OK
            else
                if grep -q 'peripheral not found' tmp/$peri/$f.err; then
                    echo No Peripheral
                else
                    echo OTHER FAILURE
                fi
                rm tmp/$peri/$f.yaml
            fi
        done
    ;;
    gen)
        rm -rf build/data
        cargo run -p py32-data-gen && cargo run -p py32-metapac-gen
    ;;
    ci)
        echo TODO $CMD
    ;;
    *)
        echo "unknown command"
    ;;
esac

