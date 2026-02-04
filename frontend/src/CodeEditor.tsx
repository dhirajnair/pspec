import { useMemo } from 'react';
import CodeMirror from '@uiw/react-codemirror';
import { python } from '@codemirror/lang-python';
import { EditorView, lineNumbers, Decoration, ViewPlugin } from '@codemirror/view';
import { Facet } from '@codemirror/state';

interface CodeEditorProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  highlightedLine?: number | null;
}

const highlightLineFacet = Facet.define<number | null>();

const highlightPlugin = ViewPlugin.fromClass(
  class {
    decorations = Decoration.none;
    constructor(readonly view: EditorView) {
      this.build();
    }
    update() {
      this.build();
    }
    build() {
      const values = this.view.state.facet(highlightLineFacet);
      const line = values[0] ?? null;
      if (line == null || line < 1) {
        this.decorations = Decoration.none;
        return;
      }
      const { doc } = this.view.state;
      const n = Math.min(line, doc.lines);
      const lineObj = doc.line(n);
      this.decorations = Decoration.set([
        Decoration.line({ class: 'cm-line-highlight' }).range(lineObj.from),
      ]);
    }
  },
  { decorations: (v) => v.decorations }
);

export default function CodeEditor({
  value,
  onChange,
  placeholder,
  highlightedLine = null,
}: CodeEditorProps) {
  const extensions = useMemo(
    () => [
      lineNumbers(),
      python(),
      EditorView.lineWrapping,
      highlightLineFacet.of(highlightedLine),
      highlightPlugin,
    ],
    [highlightedLine]
  );

  return (
    <div className="editor-wrap">
      <CodeMirror
        value={value}
        height="100%"
        minHeight="320px"
        placeholder={placeholder}
        extensions={extensions}
        onChange={onChange}
        basicSetup={{
          lineNumbers: true,
          foldGutter: false,
          highlightActiveLine: true,
        }}
      />
    </div>
  );
}
