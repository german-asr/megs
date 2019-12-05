import os
import click
from audiomate.corpus import io


@click.command()
@click.argument('download_folder', type=click.Path())
def run(download_folder):

    #
    # Common-Voice
    #

    common_voice_path = os.path.join(download_folder, 'common_voice')

    if not os.path.isdir(common_voice_path):
        print((
            'You have to download common-voice de corpus manually '
            'to data/download/common_voice!'
        ))
        exit(0)

    #
    # Voxforge
    #

    voxforge_path = os.path.join(download_folder, 'voxforge')

    if not os.path.isdir(voxforge_path):
        print('Download Voxforge')
        os.makedirs(voxforge_path, exist_ok=True)
        voxforge_dl = io.VoxforgeDownloader(lang='de', num_workers=8)
        voxforge_dl.download(voxforge_path)
    else:
        print('Voxforge already exists')

    #
    # TUDA
    #

    tuda_path = os.path.join(download_folder, 'tuda')

    if not os.path.isdir(tuda_path):
        print('Download TUDA')
        os.makedirs(tuda_path, exist_ok=True)
        tuda_dl = io.TudaDownloader()
        tuda_dl.download(tuda_path)
    else:
        print('TUDA already exists')

    #
    # SWC
    #

    swc_path = os.path.join(download_folder, 'swc')

    if not os.path.isdir(swc_path):
        print('Download SWC')
        os.makedirs(swc_path, exist_ok=True)
        swc_dl = io.SWCDownloader()
        swc_dl.download(swc_path)
    else:
        print('SWC already exists')

    #
    # M-AILABS
    #

    mailabs_path = os.path.join(download_folder, 'mailabs')

    if not os.path.isdir(mailabs_path):
        print('Download Mailabs')
        os.makedirs(mailabs_path, exist_ok=True)
        mailabs_dl = io.MailabsDownloader(tags=['de_DE'])
        mailabs_dl.download(mailabs_path)
    else:
        print('Mailabs already exists')


if __name__ == '__main__':
    run()
