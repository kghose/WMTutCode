"""This program uses matplotlib to generate an interactive corsi blocks game.
We use a class to implement the game because we need to carry around a bunch of metadata that things like onlick
need to access.

The display of the corsi blocks occurs within a single method run_corsi which reads in the current difficulty level and then generates a sequence of blocks which it then proceeds to display. At the end of the display it sets up a simple sequence counter that points to which corsi block we are at (the 1st one) and waits for mouse presses on the main screen. Pressing any of the menu items aborts the trial just displayed and executes the menu item. Clicking on the main screen tests to see if the click is on an appropriate block. If it is not, feedback is given and the next trial is started. If the block is appropriate then we move the counter along until all blocks are done, at which point we give feed back and start the next trial.

To generate app on mac

python ~/bin/pyinstaller-2.0/pyinstaller.py -F -w -y corsiblocks.py

TODO: Implement staircase method and give realtime feedback at bottom as a strip chart and current threshold value
"""
import matplotlib
matplotlib.use('macosx')
import matplotlib.animation as animation
import pylab, time

class CorsiBlocks:
  def __init__(self):
    self.setup_main_screen()
    self.ani = None
    self.span = 2 #How many block
    self.in_trial = False
    self.showing_sequence = False
    self.showing_period = False
    self.streak = 0
    self.staircase_streak = 2 #How many corrects before we increase difficulty
    self.span_history = [] #Our trial results

  def setup_main_screen(self):
    self.fig = pylab.figure(figsize=(6,8))
    pylab.subplots_adjust(top=.95, bottom=0.05, left=.05, right=.95, hspace=.15, wspace=.15)
    pylab.suptitle('Corsi Blocks')

    rows = 10
    cols = 8

    self.ax = {}
    #Main corsi blocks display
    self.ax['main'] = pylab.subplot2grid((rows, cols), (0, 0), colspan=cols, rowspan=rows-1)
    self.clear_main_screen('Move the mouse out of this panel to start\nA sequence of blocks will appear\nAt the end of the sequence\nThe panel will change color\nClick on the blocks in the order they appeared.')

    #The staircase display with span estimate
    self.ax['staircase'] = pylab.subplot2grid((rows, cols), (9, 1), colspan=cols-1)
    pylab.setp(self.ax['staircase'], 'xticks', [], 'yticks', [])
    self.cid = self.fig.canvas.mpl_connect('button_press_event', self.onclick)
    self.cid2 = self.fig.canvas.mpl_connect('axes_leave_event', self.onleaveaxes)
    self.cid3 = self.fig.canvas.mpl_connect('axes_enter_event', self.onenteraxes)


  def clear_main_screen(self, msg=None):
    ax = self.ax['main']
    ax.cla()
    pylab.setp(ax,'xlim', [-1, 5], 'ylim', [-1, 5], 'xticks', [], 'yticks', [])
    if msg is not None:
      ax.text(2,2,msg,horizontalalignment='center')

  def onleaveaxes(self, event):
    if event.inaxes == self.ax['main']:
      if not self.in_trial:
        self.start_session()

  def onenteraxes(self, event):
    if event.inaxes == self.ax['main']:
      if self.showing_sequence:
        self.abort_session()

  def block_sequence(self):
    for n in self.this_sequence:
      x = n%5
      y = n/5
      yield x,y

  def draw_sequence_frame(self):
    ax = self.ax['main']
    ax.patch.set_facecolor('w')
    try:
      x,y = self.bs_gen.next()
      h = ax.plot(x,y,'ks',ms=25)
      self.block_h.append(h)
    except StopIteration:
      self.event_source.callbacks = []
      self.showing_sequence = False
      ax.patch.set_facecolor('gray')
    finally:
      pylab.draw()


  def start_session(self):
    self.in_trial = True
    self.current_block = 0
    self.showing_sequence = True
    bc = self.span
    idx = pylab.arange(5*5) #we work on a 5,5 square
    pylab.shuffle(idx)
    self.this_sequence = idx[:bc] #Sequence of blocks
    self.bs_gen = self.block_sequence() #Need to convert it into a generator
    self.block_h = []
    self.event_source = self.fig.canvas.new_timer(interval=1000)
    self.event_source.add_callback(self.draw_sequence_frame)
    self.clear_main_screen()
    self.event_source.start()

  def abort_session(self):
    self.event_source.callbacks = []
    self.clear_main_screen('Wait for the screen to change color\nbefore starting your answer.\nMove mouse out of area to continue')
    ax = self.ax['main']
    ax.patch.set_facecolor('r')
    self.showing_sequence = False
    self.in_trial = False
    pylab.draw()

  def test_block(self, event):
    x = event.xdata
    y = event.ydata
    idx = self.this_sequence
    cx = idx[self.current_block]%5
    cy = idx[self.current_block]/5
    if ((x-cx)**2 < .25) and ((y-cy)**2 < .25):
      self.block_h[self.current_block][0].set_markerfacecolor('b')
      pylab.draw()
      self.current_block += 1
      if self.current_block == idx.size:
        self.trial_correct(True)
    else:
      self.trial_correct(False)

  def trial_correct(self, result):
    if result:
      msg = 'Correct!\nMove mouse out of area to continue'
      self.streak += 1
      self.span_history.append(self.span)
      if self.streak >= self.staircase_streak:
        self.span += 1
        self.streak = 0
    else:
      msg = 'Wrong :(\nMove mouse out of area to continue'
      self.streak = 0
      self.span = max(1, self.span - 1)

    self.clear_main_screen(msg)
    self.plot_span_history()
    self.in_trial = False
    pylab.draw()

  def plot_span_history(self):
    sh = self.span_history
    l = max(-10, -len(sh))
    my_span = sum(sh[l:])/float(-l)
    ax = self.ax['staircase']
    ax.cla()
    ax.plot(sh,'k.')
    ax.plot([0, len(sh)-1], [my_span, my_span], 'k:')
    pylab.xlabel('Trials')
    pylab.ylabel('Span')
    pylab.setp(ax, 'xlim', [-.5, 1.1*(len(sh)-1)], 'ylim', [0, max(sh)+.5], 'xticks', [len(sh)-1], 'yticks', [my_span], 'yticklabels',['{:1.1f}'.format(my_span)], 'xticklabels', [len(sh)])

  def onclick(self, event):
    if event.inaxes == self.ax['main']:#We clicked on main screen
      if self.in_trial:
        if self.showing_sequence:#test if our stim presentation is still running
          #To be harsh, we should abort the trial, we just ignore it
          return
        else: #We are in a trial, and have finished stim presentation
          self.test_block(event)

cb = CorsiBlocks()
pylab.show()