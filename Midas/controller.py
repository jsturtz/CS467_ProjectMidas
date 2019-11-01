import docker
import click
import os


@click.command()
@click.argument('image')
@click.argument('args', nargs=-1)
def main(image, args):

    # make the shared directory
    try:
        os.makedirs(f'{os.getcwd()}/{image}/data')
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

    client = docker.from_env()

    try:
        # check if the image already exists, no need to rebuild
        docker_img = client.images.get(image)
    except docker.errors.ImageNotFound:
        # find the location of the image
        # build
        print('image not found')
        docker_img = client.images.build(path=f"{os.getcwd()}/{image}/.")

    # run
    try:
        client.containers.run(
            docker_img[0],
            ['python', 'main.py'] + list(args),
            network="databases_default",
            volumes={f'{os.getcwd()}/{image}/data/': {'bind': '/var/tmp/', 'mode': 'rw'}}
        )
        return 0
    except:  # catch all errors (container or task)
        return 1


if __name__ == "__main__":
    main()
